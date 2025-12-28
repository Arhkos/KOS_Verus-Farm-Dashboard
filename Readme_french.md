# 📱 KOS Verus Farm Dashboard

Un tableau de bord de monitoring temps réel haute performance, conçu pour la gestion centralisée et le diagnostic avancé des fermes de minage mobiles Verus (VRSC).

## 🖼️ Aperçu de l'interface

Voici un aperçu de la console de monitoring en action, affichant la grille des mineurs et les statistiques globales sur une seule ligne.

## ✨ Fonctionnalités Clés

- **Interface Ultra-Compacte (v3.0)** : Header optimisé sur une seule ligne fusionnant titre, filtres et totaux pour laisser un maximum d'espace à la grille de mineurs.

- **Synchronisation Hybride** : Comparaison instantanée entre le hashrate rapporté par le téléphone (RPC) et le hashrate réel détecté par le pool **Vipor.net**.

- **Gestion Réseau Étendue** : Support natif des masques de sous-réseaux larges (ex: `/23` pour gérer jusqu'à 512 IPs) grâce à l'intégration de la bibliothèque `ipaddress`.

- **Filtrage Dynamique et Persistant** : Isolation instantanée des mineurs par statut. Le filtre reste mémorisé par le navigateur (`localStorage`) même après un rafraîchissement automatique.

- **Calcul d'Efficacité Globale** : Badge dédié affichant le pourcentage de rendement réel (Total Pool / Total Local) pour identifier les pertes réseau ou les "stale shares".

- **Historique de Santé** : Suivi visuel des 3 derniers cycles de scan avec horodatage complet (`HH:MM:SS`) pour surveiller la stabilité de la ferme.

---

## 📋 Prérequis

Avant d'installer et de lancer le dashboard, assurez-vous de disposer des éléments suivants :

- **Python 3.8+** : Le script utilise des bibliothèques modernes comme `ipaddress` et `threading`.

- **Mineurs configurés** : Vos téléphones doivent faire tourner un mineur compatible (ex: CCMiner) avec le **port RPC 4068** ouvert et accessible sur votre réseau local.

- **Accès réseau** : La machine qui héberge le dashboard doit pouvoir "pinger" les mineurs sur la plage IP définie.

- **URL API Vipor** : Vous devez disposer de l'adresse de votre wallet sur le pool Vipor pour récupérer les statistiques distantes.

- **Bibliothèques Python** : L'installation nécessite les modules `flask` et `requests`.

Parfait, passons au **Chapitre 6 : Configuration**. C'est la partie la plus importante pour que le script fonctionne correctement chez l'utilisateur final.

Voici le contenu à copier :

---

## ⚙️ Configuration

Le paramétrage se fait en deux étapes : la liste de vos appareils et les réglages du script.

### 1. Fichier des mineurs (`MINER_NAMES.csv`)

Créez un fichier nommé **`MINER_NAMES.csv`** à la racine du projet. Ce fichier fait le lien entre l'adresse IP locale de vos téléphones et le nom que vous voyez sur la Pool.

**Format requis :**

> **Attention** : Utilisez impérativement le point-virgule (`;`) comme séparateur.

### 2. Variables du script

Ouvrez le fichier `miner_web_dashboard.py` avec un éditeur de texte et modifiez les variables suivantes dans la section `--- CONFIGURATION ---` :

- **`NETWORK_MASK`** : Définissez votre plage réseau. Le script gère les masques larges comme le `/23` (ex: `172.16.0.0/23`).

- **`POOL_API_URL`** : Collez l'adresse API de votre adresse de portefeuille (Vipor REST API).

- **`DIFF_THRESHOLD`** : Seuil de tolérance (ex: `0.3`). Augmentez cette valeur (ex: `0.5`) si vous voulez être moins sensible aux alertes de différence de Hashrate (Violet).

---

## 🚦 Guide de l'Interface (Légende)

Le dashboard utilise un code couleur intuitif pour vous permettre d'identifier les problèmes de votre ferme en un coup d'œil :

### 🟢 Statut OK (Vert)

Tout est nominal. Le téléphone fonctionne à sa pleine capacité, tous les cœurs CPU sont actifs et le hashrate rapporté par le pool est en adéquation avec la production locale.

### 🟡 Statut WARN (Jaune)

Une anomalie légère est détectée. Cela peut signifier qu'un ou plusieurs cœurs du processeur sont inactifs (souvent dû à une surchauffe/throttling) ou que le script est en attente de la première réponse du mineur.

### 🟣 Statut DIFF (Violet)

**Alerte Efficacité** : Il existe un écart majeur entre le hashrate local et celui vu par le pool. C'est l'indicateur idéal pour repérer une mauvaise connexion Wi-Fi ou un taux de rejet (stale shares) trop élevé.

### 🔵 Statut GHOST (Bleu)

**Mineur Fantôme** : Ce mineur est actif sur votre compte Vipor mais est introuvable sur votre réseau local. Cela se produit si vous avez des mineurs externes ou si un téléphone a changé d'adresse IP.

### 🔴 Statut OFF (Rouge)

**Critique** : L'appareil est injoignable sur le réseau local. Le téléphone est probablement éteint, déconnecté, ou l'application de minage a crashé.

---

## 🚀 Lancement

Une fois la configuration terminée, vous pouvez démarrer votre tableau de bord en une seule commande.

### 1. Démarrer le serveur

Lancez le script principal depuis votre terminal ou invite de commande :

### 2. Accéder à l'interface

Ouvrez votre navigateur web (Chrome, Firefox ou Edge recommandés) et rendez-vous à l'adresse suivante :

- **Sur la machine locale** : `http://localhost:5000`

- **Depuis un autre appareil du réseau** : `http://[IP_DE_VOTRE_SERVEUR]:5000`

### 🔄 Rafraîchissement Automatique

Le tableau de bord est conçu pour fonctionner en continu. Il met à jour les données automatiquement. Vous pouvez laisser l'onglet ouvert sur un écran de contrôle, les filtres que vous avez sélectionnés resteront actifs grâce à la persistance d'état.

Pour conclure ce document, voici le **Chapitre 9 : Structure du projet**. Il permet aux utilisateurs de comprendre l'organisation des fichiers et de savoir où intervenir s'ils veulent personnaliser l'outil.

Voici le contenu à copier :

---

## 📂 Structure du projet

Voici l'organisation des fichiers du dépôt :

- **`miner_web_dashboard.py`** : Le script Python principal. Il contient à la fois le moteur de scan réseau et le serveur web Flask.

- **`MINER_NAMES.csv`** : Votre base de données locale (IP et Noms). Ce fichier est nécessaire pour le bon affichage des mineurs.

- **`requirements.txt`** : Liste des bibliothèques nécessaires pour installer l'environnement en une commande.

- **`docs/`** : Dossier contenant les ressources de la documentation, notamment les captures d'écran de l'interface.

- **`.gitignore`** : Fichier de configuration pour éviter d'envoyer vos fichiers personnels (comme votre CSV de mineurs) sur un dépôt public GitHub.

- **`README.md`** : Ce document d'explication.
