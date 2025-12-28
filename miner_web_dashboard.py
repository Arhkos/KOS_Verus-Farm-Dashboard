import socket
import threading
import csv
import os
import time
import requests
import ipaddress
from flask import Flask, render_template_string, jsonify, send_from_directory

# --- CONFIGURATION ---
CSV_FILE = "MINER_NAMES.csv"
PORT_RPC = 4068
NETWORK_MASK = "192.168.1.0/24" 
WEB_PORT = 5000 
SCAN_INTERVAL = 30 
POOL_API_URL = "https://restapi.vipor.net/api/pools/verus/miners/YOUR_ADDRESS_HERE"
DIFF_THRESHOLD = 0.5 

app = Flask(__name__)

# --- ETAT GLOBAL ---
failure_counter = {}
scan_history = []
pool_stats = {} 
farm_data = {
    "results": [], "total_khs": 0, "total_pool_mhs": 0, "efficiency": 0,
    "last_update": "", "active_count": 0, "history": [],
    "stats": {"ok": 0, "warning": 0, "diff": 0, "ghost": 0, "error": 0}
}

def load_miner_names():
    names = {}
    if not os.path.exists(CSV_FILE): return names
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            if reader.fieldnames:
                reader.fieldnames = [n.strip().upper() for n in reader.fieldnames]
            for row in reader:
                ip, nom = row.get('IP'), row.get('NOM')
                if ip and nom: names[ip.strip()] = nom.strip()
    except: pass
    return names

def get_rpc_data(ip, command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.6)
            s.connect((ip, PORT_RPC))
            s.sendall(command.encode())
            response = ""
            while True:
                chunk = s.recv(4096).decode('utf-8')
                if not chunk: break
                response += chunk
            return response
    except: return None

def update_pool_stats():
    global pool_stats
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(POOL_API_URL, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            new_stats = {}
            workers = data.get('performance', {}).get('workers', {})
            for w_name, w_info in workers.items():
                hr_raw = w_info.get('hashrate', 0)
                new_stats[w_name] = round(float(hr_raw) / 1000000, 2)
            pool_stats = new_stats
            print(f"[*] API Vipor OK : {len(pool_stats)} mineurs extraits.")
    except: pass

def background_scanner():
    global farm_data, failure_counter, scan_history
    update_pool_stats()
    last_pool_update = time.time()

    while True:
        names_map = load_miner_names()
        if time.time() - last_pool_update > 120:
            update_pool_stats()
            last_pool_update = time.time()

        temp_results = {}
        threads_list = []
        network = ipaddress.ip_network(NETWORK_MASK, strict=False)
        target_ips = [ip for ip in names_map.keys() if ipaddress.ip_address(ip) in network]

        def scan(ip):
            res = get_rpc_data(ip, 'summary')
            if res:
                t_raw = get_rpc_data(ip, 'threads')
                temp_results[ip] = {"summary": res, "threads": t_raw}

        for ip in target_ips:
            t = threading.Thread(target=scan, args=(ip,))
            threads_list.append(t)
            t.start()
        for t in threads_list: t.join()

        final_list = []
        current_total_khs = 0
        current_active_count = 0
        stats_count = {"ok": 0, "warning": 0, "diff": 0, "ghost": 0, "error": 0}
        processed_names = set()

        for ip in target_ips:
            name = names_map[ip]
            processed_names.add(name.upper())
            data = temp_results.get(ip)
            pool_hr = pool_stats.get(name, 0.0)
            
            if data:
                failure_counter[ip] = 0
                try:
                    s_raw = data["summary"].strip('|')
                    s_dict = dict(item.split('=') for item in s_raw.split(';') if '=' in item)
                    khs = float(s_dict.get('KHS', 0))
                    current_total_khs += khs
                    current_active_count += 1
                    local_mhs = khs / 1000
                    
                    active, total = 0, 0
                    if data["threads"]:
                        cores = [c for c in data["threads"].split('|') if 'KHS=' in c]
                        total = len(cores)
                        active = sum(1 for c in cores if float(dict(item.split('=') for item in c.split(';') if '=' in item).get('KHS', 0)) > 0)
                    
                    status = "ok"
                    if active < total: status = "warning"
                    if local_mhs > 0:
                        ratio = pool_hr / local_mhs
                        if ratio < (1 - DIFF_THRESHOLD) or ratio > (1 + DIFF_THRESHOLD): status = "diff"
                    if khs == 0: status = "error"

                    stats_count[status] += 1
                    final_list.append({"ip": ip, "name": name, "l_mhs": f"{local_mhs:.2f}", "p_mhs": f"{pool_hr:.2f}", "cpu": f"{active}/{total}", "status": status})
                except: pass
            else:
                failure_counter[ip] = failure_counter.get(ip, 0) + 1
                if failure_counter[ip] < 3:
                    final_list.append({"ip": ip, "name": name, "l_mhs": "...", "p_mhs": f"{pool_hr:.2f}", "cpu": "Wait", "status": "warning"})
                    stats_count["warning"] += 1
                    current_active_count += 1 
                else:
                    status = "ghost" if pool_hr > 0 else "error"
                    stats_count[status] += 1
                    final_list.append({"ip": ip, "name": name, "l_mhs": "0.00", "p_mhs": f"{pool_hr:.2f}", "cpu": "-", "status": status})

        for w_name, w_hr in pool_stats.items():
            if w_name.upper() not in processed_names:
                final_list.append({"ip": "?.?.?.?", "name": w_name, "l_mhs": "0.00", "p_mhs": f"{w_hr:.2f}", "cpu": "POOL", "status": "ghost"})
                stats_count["ghost"] += 1

        final_list.sort(key=lambda x: ipaddress.ip_address(x['ip']) if x['ip'] != "?.?.?.?" else ipaddress.ip_address("255.255.255.255"))
        
        total_l_mhs = current_total_khs / 1000
        total_p_mhs = sum(pool_stats.values())
        eff = (total_p_mhs / total_l_mhs * 100) if total_l_mhs > 0 else 0

        now_time = time.strftime("%H:%M:%S")
        scan_history.insert(0, {"time": now_time, "count": current_active_count})
        scan_history = scan_history[:3]

        farm_data = {
            "results": final_list, "total_khs": current_total_khs, "total_pool_mhs": total_p_mhs,
            "efficiency": round(eff, 1), "last_update": now_time, "active_count": current_active_count, 
            "history": scan_history, "stats": stats_count
        }
        time.sleep(SCAN_INTERVAL)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Farm Dashboard</title>
    <meta http-equiv="refresh" content="30">
<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">

    <style>
        body { font-family: sans-serif; background: #0b0e14; color: #fff; margin: 0; padding: 5px; }
        .main-header { 
            background: #1a1f2b; padding: 8px 15px; border-radius: 5px; margin-bottom: 8px; 
            border: 1px solid #2d304d; display: flex; align-items: center; justify-content: space-between; gap: 15px;
        }
        .info-group { display: flex; flex-direction: column; min-width: 140px; }
        
        .filter-bar { display: flex; gap: 5px; }
        .f-btn { border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 10px; font-weight: bold; color: #fff; background: #2d304d; border-bottom: 2px solid transparent; }
        .f-btn.active { border-bottom-color: #fff; background: #3d405d; }
        .f-ok { color: #00ff88; } .f-warning { color: #ffcc00; } .f-diff { color: #ff00ff; } .f-ghost { color: #00ccff; } .f-error { color: #ff4444; }

        .stats-container { display: flex; align-items: center; gap: 15px; }
        .stat-item { text-align: right; }
        .s-label { font-size: 9px; color: #8892b0; text-transform: uppercase; display: block; margin-bottom: -4px; }
        .s-val { font-size: 22px; font-weight: 900; }
        .s-local { color: #00ff88; } .s-pool { color: #00ccff; } .s-eff { color: #ffcc00; font-size: 18px; }

        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(92px, 1fr)); gap: 5px; }
        .card { background: #1a1f2b; padding: 4px; border-radius: 4px; border: 1px solid #2d304d; text-align: center; border-top: 3px solid #444; }
        .card.ok { border-top-color: #00ff88; } .card.warning { border-top-color: #ffcc00; }
        .card.diff { border-top-color: #ff00ff; background: #261226; } .card.error { border-top-color: #ff4444; opacity: 0.6; }
        .card.ghost { border-top-color: #00ccff; background: #122226; }
        
        .name { font-size: 9px; color: #a0a8c0; font-weight: bold; white-space: nowrap; overflow: hidden; }
        .l-mhs { color: #fff; font-weight: bold; font-size: 11px; display:block; margin: 1px 0;}
        .p-mhs { color: #00ccff; font-size: 10px; }
        .cpu { font-size: 8px; color: #8892b0; }
        .ip { font-size: 8px; color: #5c637a; border-top: 1px solid #252a3d; margin-top: 2px; }
        .history-tag { font-size: 9px; background: #2d304d; padding: 1px 3px; border-radius: 2px; color: #8892b0; }
    </style>
</head>
<body>
    <div class="main-header">
        <div class="info-group">
            <b style="font-size:13px; color:#8892b0;">{{ data.last_update }} | {{ data.active_count }} ACTIFS</b><div style="margin-top:2px; display:flex; gap:3px; flex-wrap: wrap;">
    {% for h in data.history %}
        <span class="history-tag" style="font-family: monospace;">
            {{ h.time }} <small style="font-weight: bold;">({{ h.count }})</small>
        </span>
    {% endfor %}
</div>
        </div>

<div class="filter-bar">
    <button id="btn-all" class="f-btn active" onclick="filterCards('all', this)">ALL ({{ data.results|length }})</button>
    <button id="btn-ok" class="f-btn f-ok" onclick="filterCards('ok', this)">OK ({{ data.stats.ok }})</button>
    <button id="btn-warning" class="f-btn f-warning" onclick="filterCards('warning', this)">WARN ({{ data.stats.warning }})</button>
    <button id="btn-diff" class="f-btn f-diff" onclick="filterCards('diff', this)">DIFF ({{ data.stats.diff }})</button>
    <button id="btn-ghost" class="f-btn f-ghost" onclick="filterCards('ghost', this)">GHOST ({{ data.stats.ghost }})</button>
    <button id="btn-error" class="f-btn f-error" onclick="filterCards('error', this)">OFF ({{ data.stats.error }})</button>
</div>

        <div class="stats-container">
            <div class="stat-item"><span class="s-label">Efficiency</span><span class="s-val s-eff">{{ data.efficiency }}%</span></div>
            <div class="stat-item"><span class="s-label">Local</span><span class="s-val s-local">{{ (data.total_khs / 1000) | round(2) }}</span></div>
            <div class="stat-item"><span class="s-label">Vipor</span><span class="s-val s-pool">{{ data.total_pool_mhs | round(2) }}</span></div>
        </div>
    </div>

    <div class="grid" id="minerGrid">
        {% for m in data.results %}
        <div class="card {{ m.status }}" data-status="{{ m.status }}">
            <div class="name">{{ m.name }}</div>
            <span class="l-mhs">L: {{ m.l_mhs }}</span>
            <span class="p-mhs">P: {{ m.p_mhs }}</span>
            <div class="cpu">{{ m.cpu }}</div>
            <div class="ip">{{ m.ip }}</div>
        </div>
        {% endfor %}
    </div>

<script>
    // Fonction principale de filtrage
    function filterCards(status, btn) {
        // Sauvegarde le choix dans le navigateur
        localStorage.setItem('activeFilter', status);

        // UI : Gestion de la classe active sur les boutons
        document.querySelectorAll('.f-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // UI : Masquage/Affichage des cartes
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            if (status === 'all') { 
                card.style.display = 'block'; 
            } else { 
                card.style.display = (card.getAttribute('data-status') === status) ? 'block' : 'none'; 
            }
        });
    }

    // Au chargement de la page, on restaure le filtre précédent
    window.onload = function() {
        const savedFilter = localStorage.getItem('activeFilter') || 'all';
        const targetBtn = document.getElementById('btn-' + savedFilter);
        if (targetBtn) {
            filterCards(savedFilter, targetBtn);
        }
    };
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, data=farm_data)

@app.route('/favicon.ico')
def favicon(): 
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    threading.Thread(target=background_scanner, daemon=True).start()
    app.run(host='0.0.0.0', port=WEB_PORT)