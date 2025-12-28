![image](https://raw.githubusercontent.com/Arhkos/KOS_Verus-Farm-Dashboard/refs/heads/main/static/Logo.png "Logo")

## 📱 Verus Farm Dashboard

A high-performance, real-time monitoring dashboard designed for centralized management and advanced diagnostics of large-scale Verus (VRSC) mobile mining farms.

---

### 🚩 Why this project?

Monitoring a large fleet of smartphones (170+ devices) presents unique challenges: network instability, CPU throttling, and discrepancies between local hashrate and pool reporting.

This dashboard was developed to provide a **single source of truth**, merging raw data from miners with real-time statistics from the **Vipor.net** pool API, all within an interface optimized for operational efficiency.

---

## 🖼️ Interface Preview

Here is a look at the monitoring console in action, showing the miner grid and global statistics on a single line.

![image](https://raw.githubusercontent.com/Arhkos/KOS_Verus-Farm-Dashboard/refs/heads/main/docs/Screenshot.png "screenshot")

---

## ✨ Key Features

- **Ultra-Compact Interface (v3.0)**: Optimized single-line header merging titles, filters, and totals to maximize screen real estate for the miner grid.

- **Hybrid Synchronization**: Real-time comparison between hashrate reported by the device (RPC) and actual hashrate detected by the **Vipor.net** pool.

- **Extended Network Support**: Native support for large subnet masks (e.g., `/23` to manage up to 512 IPs) using the `ipaddress` library.

- **Dynamic & Persistent Filtering**: Instant isolation of miners by status. Filter selection is saved in the browser (`localStorage`) and persists after auto-refreshes.

- **Global Efficiency Calculation**: Dedicated badge showing the real yield percentage (Total Pool / Total Local) to identify network losses or stale shares.

- **Health History**: Visual tracking of the last 3 scan cycles with full timestamps (`HH:MM:SS`) to monitor farm stability.

---

## 📋 Prerequisites

Before installing and launching the dashboard, ensure you have the following:

- **Python 3.8+**: The script uses modern libraries like `ipaddress` and `threading`.

- **Configured Miners**: Your phones must run a compatible miner (e.g., CCMiner) with **RPC port 4068** open and accessible on your local network.

- **Network Access**: The machine hosting the dashboard must be able to "ping" the miners on the defined IP range.

- **Vipor API URL**: You need your wallet address API URL from the Vipor pool to fetch remote stats.

- **Python Libraries**: Installation requires `flask` and `requests`.

---

## 🛠️ Installation

Follow these steps to install the project on your local machine:

### 1. Clone the project

### 2. Install Python : https://www.python.org/downloads/windows/ or linux version

### 3. Install Dependencies

The script requires **Flask** (web server) and **Requests** (API polling). Install them directly using `pip`:

```powershell
python pip install flask
```

To check if installed : 

```powershell
pip install list
```

---

## ⚙️ Configuration

Setup is done in two steps: your device list and the script settings.

### 1. Miner List (`MINER_NAMES.csv`)

Create a file named **`MINER_NAMES.csv`** in the root directory. This file maps your phones' local IP addresses to their Worker Names on the pool.

**Required Format:**

> **Important**: Use the semicolon (`;`) as the separator.

### 2. Script Variables

Open `miner_web_dashboard.py` and modify the following variables in the `--- CONFIGURATION ---` section:

- **`NETWORK_MASK`**: Define your network range (e.g., `172.16.0.0/23`).

- **`POOL_API_URL`**: Paste your Vipor Wallet REST API URL.

- **`DIFF_THRESHOLD`**: Tolerance threshold (e.g., `0.3`). Increase this (e.g., `0.5`) to be less sensitive to hashrate difference alerts (Purple).

---

## 🚦 Interface Guide (Legend)

The dashboard uses intuitive color coding to help you identify issues at a glance:

### 🟢 OK Status (Green)

Everything is nominal. The phone is running at full capacity, all CPU cores are active, and the pool hashrate matches local production.

### 🟡 WARN Status (Yellow)

A minor anomaly is detected. This usually means one or more CPU cores are inactive (often due to heat/throttling) or the script is waiting for the first miner response.

### 🟣 DIFF Status (Purple)

**Efficiency Alert**: There is a major gap between local hashrate and pool hashrate. Ideal for spotting poor Wi-Fi connections or high stale share rates.

### 🔵 GHOST Status (Blue)

**Ghost Miner**: This miner is active on your Vipor account but cannot be found on your local network. Happens with external miners or if a phone's IP changed.

### 🔴 OFF Status (Red)

**Critical**: The device is unreachable on the local network. The phone is likely off, disconnected, or the mining app has crashed.

---

## 🚀 Usage

### 1. Start the Server

Run the main script from your terminal:

### 2. Access the Interface

Open your web browser and navigate to:

- **Local machine**: `http://localhost:5000`

- **Other network device**: `http://[YOUR_SERVER_IP]:5000`

---

#### 📂 Project Structure

- **`miner_web_dashboard.py`**: Main Python script (Network scanner + Flask server).

- **`MINER_NAMES.csv`**: Local database (IPs and Names).

- **`static/`**: Folder containing the **favicon.ico** and other static assets.

- **`requirements.txt`**: List of required Python libraries.

- **`docs/`**: Folder for documentation assets (screenshots).

- **`.gitignore`**: Prevents personal files from being uploaded to GitHub.

- **`README.md`**: This documentation file.