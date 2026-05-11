# 🐄 Plateforme IoT de Surveillance de Bétail - LoRaWAN

> **Projet de Module PLATEFORMES ET TECHNOLOGIES DE L'IOT**  
> EL BOUYED Zainab & NASR Houda 

Plateforme complète de surveillance en temps réel de bovins laitiers via un réseau LoRaWAN, avec simulation de données issues de datasets scientifiques réels et dashboard web interactif.

---

## 📌 Table des matières

- [Aperçu](#-aperçu)
- [Architecture](#-architecture)
- [Structure du projet](#-structure-du-projet)
- [Datasets](#-datasets)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Format des données](#-format-des-données)
- [Encodage Cayenne LPP](#-encodage-cayenne-lpp)
- [Dashboard](#-dashboard)
- [Configuration TTN](#-configuration-ttn)

---

## 🌟 Aperçu

Le système surveille **4 vaches** en temps réel en transmettant toutes les **10 secondes** :
- 🌡️ La **température corporelle** (seuil d'alerte fièvre : 39,5°C)
- 📐 L'**accélération 3 axes** (détection chute, chaleurs, rumination)
- 📍 La **position GPS** (géolocalisation autour de Casablanca)

Les données transitent via **LoRaWAN → TTN → Webhook → Dashboard Flask**.

| État | Couleur | Température | Alerte |
|------|---------|-------------|--------|
| ✅ Saine | 🟢 Vert | 38,0 – 39,0°C | Aucune |
| 🔥 Chaleurs | 🟡 Orange | 38,5 – 39,5°C | Email + Push |
| 🚨 Fièvre | 🔴 Rouge | > 39,5°C | SMS + Push |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     COUCHE EDGE                             │
│  DS18B20 (1-Wire) + MPU6050 (I2C) + GPS L76 (UART)         │
│           └──► STM32L072 + SX1276 ──► LoRa 868 MHz         │
└───────────────────────────┬─────────────────────────────────┘
                            │ LoRa CSS 868 MHz
┌───────────────────────────▼─────────────────────────────────┐
│                     COUCHE RÉSEAU                           │
│         Gateway RAK7258 ──► TTN (OTAA + AES-128)           │
│              décodage Cayenne LPP ──► Webhook HTTPS         │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP POST JSON
┌───────────────────────────▼─────────────────────────────────┐
│                   COUCHE PLATEFORME                         │
│    simulateur.py ──► data.json ──► dashboard.py (Flask)     │
│         └──► Graphes Chart.js + Carte Leaflet.js            │
└─────────────────────────────────────────────────────────────┘
```

**En simulation** (ce dépôt) : `simulateur.py` remplace le matériel physique en injectant les données des datasets directement dans TTN via l'API REST.

---

## 📁 Structure du projet

```
Projet_IoT_Betail/
│
├── simulateur.py          # Charge les datasets, encode en Cayenne LPP, envoie à TTN
├── dashboard.py           # Serveur Flask — dashboard web temps réel
├── data.json              # Fichier de communication entre les deux scripts
│
└── datasets/
    ├── health/            # Dataset 1 — États de santé bovins
    │   ├── healthy.csv        → Vache saine (38,0–39,0°C)
    │   ├── fever.csv          → Fièvre (40,0–41,5°C)
    │   ├── heating.csv        → Chaleurs/oestrus (38,5–39,5°C)
    │   └── salmonellosis.csv  → Salmonellose (40,0–41,0°C)
    │
    └── mmcows/            # Dataset 2 — MmCows NeurIPS 2024 (Purdue University)
        ├── T01_acceleration.csv   → Accélération IMU réelle 10 Hz (m/s²)
        └── T01_uwb.csv            → Position UWB 3D réelle (cm)
```

---

## 📊 Datasets

### Dataset 1 — cow-health-vital-signs
- **Source** : [uxeer/cow-health-vital-signs](https://github.com/uxeer/cow-health-vital-signs) — Licence MIT
- **Contenu** : 4 fichiers CSV × 22 000 lignes chacun
- **Colonnes** : `Timestamp, Temperature, SpO2, BPM, (condition)`
- **Usage dans le code** : seule la colonne `Temperature` est extraite

| Fichier | État | Plage température |
|---------|------|-------------------|
| `healthy.csv` | Vache saine | 38,0 – 39,0°C |
| `fever.csv` | Fièvre | 40,0 – 41,5°C |
| `heating.csv` | Chaleurs (oestrus) | 38,5 – 39,5°C |
| `salmonellosis.csv` | Salmonellose | 40,0 – 41,0°C |

### Dataset 2 — MmCows (NeurIPS 2024)
- **Source** : [neis-lab/mmcows](https://github.com/neis-lab/mmcows) — Licence MIT
- **Données** : 10 vaches Holstein adultes (T01–T10), 14 jours (21 juillet – 4 août 2023), Purdue University
- **T01_acceleration.csv** : accélération IMU à 10 Hz en m/s² (axes X, Y, Z) + magnétomètre
- **T01_uwb.csv** : positions UWB 3D en centimètres (localisation indoor haute précision)

> Les coordonnées UWB (cm) sont converties en degrés GPS autour de Casablanca (`LAT_REF=33.5731, LON_REF=-7.5898`) dans le simulateur.

---

## ⚙️ Installation

### Prérequis

- Python 3.8+
- Un compte [The Things Network (TTN)](https://www.thethingsnetwork.org/) avec une application et 4 devices enregistrés

### Installation des dépendances

```bash
pip install pandas numpy requests flask
```

### Configuration TTN

Dans `simulateur.py`, modifier :

```python
TTN_APP_ID  = "votre-application-id"
TTN_API_KEY = "votre-api-key"
TTN_REGION  = "eu1"  # ou us915, au915 selon votre région
```

Les 4 devices TTN doivent correspondre aux IDs :
```python
VACHES = [
    {"id": "Marguerite", "device": "collier-bovin-01", ...},
    {"id": "Rosalie",    "device": "collier-bovin-02", ...},
    {"id": "Blanchette", "device": "collier-bovin-03", ...},
    {"id": "Noisette",   "device": "collier-bovin-04", ...},
]
```

---

## 🚀 Utilisation

Lancer les deux scripts dans deux terminaux séparés, depuis le dossier `Projet_IoT_Betail/` :

**Terminal 1 — Simulateur**
```bash
python simulateur.py
```

**Terminal 2 — Dashboard**
```bash
python dashboard.py
```

Ouvrir le navigateur sur : **http://localhost:5000**

### Sortie du simulateur

```
=======================================================
  SIMULATEUR IoT — 4 Vaches dynamiques
=======================================================
  ✓ Marguerite → collier-bovin-01 (début: healthy)
  ✓ Rosalie    → collier-bovin-02 (début: fever)
  ✓ Blanchette → collier-bovin-03 (début: heating)
  ✓ Noisette   → collier-bovin-04 (début: salmonellosis)

Envoi automatique toutes les 10s | Ctrl+C pour arrêter
-------------------------------------------------------
  ✅ Marguerite | 38.5°C | healthy
  ✅ Rosalie    | 41.0°C | fever ⚠️ FIEVRE!
  ✅ Blanchette | 39.1°C | heating 🔥 Chaleurs
  ✅ Noisette   | 40.3°C | fever ⚠️ FIEVRE!
  ── Cycle 1 | Dashboard: http://localhost:5000
```

---

## 📄 Format des données — data.json

Fichier écrasé à chaque cycle (toutes les 10s). Tableau de 4 objets :

```json
[
  {
    "id": "Marguerite",
    "temp": 38.5,
    "ax": -0.52,
    "ay": -0.17,
    "az": -0.79,
    "lat": 33.5724,
    "lon": -7.5931,
    "scenario": "healthy",
    "state": "ok"
  }
]
```

| Champ | Type | Description |
|-------|------|-------------|
| `id` | string | Nom de la vache |
| `temp` | float | Température corporelle en °C (arrondie à 1 décimale) |
| `ax/ay/az` | float | Accélération X/Y/Z en **g** (MmCows converti depuis m/s²) |
| `lat/lon` | float | Position GPS en degrés décimaux |
| `scenario` | string | Dataset source actif : `healthy / fever / heating / salmonellosis` |
| `state` | string | `ok` (saine) / `fv` (fièvre > 39,5°C) / `ht` (chaleurs) |

---

## 🔢 Encodage Cayenne LPP

Payload de **23 octets** envoyé à TTN via l'API REST (base64) :

```
[Canal 1][Type 0x67][Temp MSB][Temp LSB]                    → 4 octets  (température × 10)
[Canal 2][Type 0x71][Ax MSB][Ax LSB][Ay MSB][Ay LSB][Az MSB][Az LSB] → 8 octets  (accél. × 1000)
[Canal 3][Type 0x88][Lat 3B][Lon 3B][Alt 3B]                → 11 octets (GPS × 10000)
```

**Pourquoi ces multiplicateurs ?**

Cayenne LPP stocke tout en entiers. La multiplication préserve la précision :
- `temp × 10` → résolution 0,1°C (ex: 38,5°C → 385)
- `accel × 1000` → résolution 0,001 g
- `lat/lon × 10000` → résolution 0,0001° (~11 m)

---

## 🌐 Dashboard

Le dashboard Flask offre :

- **Vue troupeau** : liste des 4 vaches avec code couleur (vert/orange/rouge)
- **Métriques temps réel** : température, accélération X/Y/Z
- **4 graphiques** (Chart.js) : courbe de température, accélération 3 axes, intensité de mouvement `|a| = √(ax²+ay²+az²)`, distribution des températures
- **Carte GPS** (Leaflet.js) : position en temps réel sur fond OpenStreetMap, marqueurs colorés selon l'état de santé
- **Panneau notifications** : alertes fièvre et chaleurs horodatées
- **Polling toutes les 5 secondes** via `fetch('/api/cows')`
- **Fenêtre glissante de 30 mesures** dans les graphiques

### Routes Flask

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Dashboard HTML complet |
| `/api/cows` | GET | Données JSON des 4 vaches (lu depuis `data.json`) |

---

## ⚡ Comportement dynamique

Pour simuler l'évolution réaliste de l'état de santé d'une vache :

- Chaque vache démarre avec un **scénario aléatoire** et un **index aléatoire** dans le CSV (entre 0 et 1000) → les 4 vaches ne sont pas synchronisées
- Toutes les **20 mesures** (~3 minutes), chaque vache change aléatoirement de scénario via `random.choice()`
- Les données d'accélération et de GPS sont **décalées temporellement** par vache (`v['idx'] + cycle`) → comportements différents à chaque instant
- Les vaches sont **séparées spatialement** sur la carte via un `offset` de 0,0003° (~33 m) par vache

---

## 📡 Configuration TTN

Le simulateur envoie des uplinks simulés à TTN via :

```
POST https://eu1.cloud.thethings.network/api/v3/as/applications/{APP_ID}/devices/{DEVICE_ID}/up/simulate
```

Paramètres radio simulés :
- **Spreading Factor** : SF7
- **Bandwidth** : 125 kHz
- **Fréquence** : 868 MHz (bande ISM Europe/Maroc)
- **Port applicatif** : f_port = 1

---

## 🔗 Références

- [The Things Network](https://www.thethingsnetwork.org/)
- [Cayenne LPP format](https://developers.mydevices.com/cayenne/docs/lora/#lora-cayenne-low-power-payload)
- [MmCows Dataset — NeurIPS 2024](https://github.com/neis-lab/mmcows)
- [cow-health-vital-signs Dataset](https://github.com/uxeer/cow-health-vital-signs)
- [RAK7258 WisGate Edge Lite](https://docs.rakwireless.com/Product-Categories/WisGate/RAK7258/)
- [B-L072Z-LRWAN1 STMicroelectronics](https://www.st.com/en/evaluation-tools/b-l072z-lrwan1.html)

---

*INPT — Institut National des Postes et Télécommunications — Rabat, Maroc*
