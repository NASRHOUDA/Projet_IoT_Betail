#!/usr/bin/env python3
"""SIMULATEUR IoT — 4 Vaches avec état dynamique selon données réelles — INPT 2025/2026"""

import pandas as pd, numpy as np, time, sys, base64, requests, json, random

LAT_REF, LON_REF, ALT_REF = 33.5731, -7.5898, 100.0

# Config TTN
TTN_APP_ID  = "surveillance-betail-inpt"
TTN_API_KEY = "NNSXS.N2SH3WQMB7L4X2GYLHKNUCZJD2YGGD5MMAXRZKY.3M7FCX2DUT2N3P5EZEA3DOEDLKZC7LA45WOZVZJYBU4JUTSBTJWA"
TTN_REGION  = "eu1"

# 4 Vaches — chacune lit TOUS les datasets et change d'état
VACHES = [
    {"id": "Marguerite", "device": "collier-bovin-01", "offset": 0},
    {"id": "Rosalie",    "device": "collier-bovin-02", "offset": 1},
    {"id": "Blanchette", "device": "collier-bovin-03", "offset": 2},
    {"id": "Noisette",   "device": "collier-bovin-04", "offset": 3},
]

def charger_tous_scenarios():
    """Charge TOUS les datasets et les fusionne en un seul tableau par vache"""
    fichiers = {
        'healthy':       'datasets/health/healthy.csv',
        'fever':         'datasets/health/fever.csv',
        'heating':       'datasets/health/heating.csv',
        'salmonellosis': 'datasets/health/salmonellosis.csv',
    }
    data = {}
    for scenario, f in fichiers.items():
        df = pd.read_csv(f)
        col = 'Temperature' if 'Temperature' in df.columns else 'temperature'
        data[scenario] = df[col].values
    return data

def charger_acc():
    df = pd.read_csv('datasets/mmcows/T01_acceleration.csv')
    return np.column_stack([df[c].values/9.81 for c in ['accel_x_mps2','accel_y_mps2','accel_z_mps2']])

def charger_gps():
    df = pd.read_csv('datasets/mmcows/T01_uwb.csv')
    return np.column_stack([LAT_REF+df['coord_y_cm'].values*0.00001,
                            LON_REF+df['coord_x_cm'].values*0.00001,
                            ALT_REF+df['coord_z_cm'].values/100.])

def get_scenario(temp):
    """Détermine le scénario selon la température"""
    if temp > 39.5:
        return "fever"
    elif 38.5 <= temp <= 39.5:
        return "heating"
    else:
        return "healthy"

def encode(t, ax, ay, az, lat, lon, alt):
    p = bytearray()
    ti = int(round(t*10))
    p.extend([1,0x67,(ti>>8)&0xFF,ti&0xFF])
    aix,aiy,aiz = int(round(ax*1000)),int(round(ay*1000)),int(round(az*1000))
    p.extend([2,0x71,(aix>>8)&0xFF,aix&0xFF,(aiy>>8)&0xFF,aiy&0xFF,(aiz>>8)&0xFF,aiz&0xFF])
    la,lo,al = int(round(lat*10000)),int(round(lon*10000)),int(round(alt*100))
    p.extend([3,0x88,(la>>16)&0xFF,(la>>8)&0xFF,la&0xFF,(lo>>16)&0xFF,(lo>>8)&0xFF,lo&0xFF,(al>>16)&0xFF,(al>>8)&0xFF,al&0xFF])
    return bytes(p)

def envoyer_ttn(device_id, payload_bytes):
    url = (f"https://{TTN_REGION}.cloud.thethings.network/api/v3"
           f"/as/applications/{TTN_APP_ID}/devices/{device_id}/up/simulate")
    headers = {"Authorization": f"Bearer {TTN_API_KEY}", "Content-Type": "application/json"}
    body = {"uplink_message": {"f_port": 1, "frm_payload": base64.b64encode(payload_bytes).decode(),
            "settings": {"data_rate": {"lora": {"spreading_factor": 7, "bandwidth": 125000}}, "frequency": "868000000"}}}
    r = requests.post(url, headers=headers, json=body)
    return r.status_code == 200

# ─── Chargement ───
print("="*55)
print("  SIMULATEUR IoT — 4 Vaches dynamiques")
print("="*55)

ALL_TEMP = charger_tous_scenarios()
ACCS = charger_acc()
GPS = charger_gps()

# Mélanger les données pour que chaque vache ait un parcours unique
for v in VACHES:
    # Chaque vache pioche dans un dataset différent au début, puis alterne
    scenarios = list(ALL_TEMP.keys())
    random.shuffle(scenarios)
    v['current_scenario'] = scenarios[0]
    v['temp_data'] = ALL_TEMP[v['current_scenario']]
    v['idx'] = random.randint(0, 1000)  # point de départ aléatoire
    print(f"  ✓ {v['id']} → {v['device']} (début: {v['current_scenario']})")

print(f"\nEnvoi automatique toutes les 10s | Ctrl+C pour arrêter\n"+"-"*55)

cycle = 0
try:
    while True:
        cycle += 1
        all_data = []
        
        for v in VACHES:
            # Changer de scénario aléatoirement toutes les ~20 mesures
            if cycle % 20 == 0:
                scenarios = list(ALL_TEMP.keys())
                v['current_scenario'] = random.choice(scenarios)
                v['temp_data'] = ALL_TEMP[v['current_scenario']]
            
            # Lire température depuis le scénario actuel
            t = v['temp_data'][v['idx'] % len(v['temp_data'])]
            v['idx'] += 1
            
            # Accélération et GPS
            a = ACCS[(v['idx'] + cycle) % len(ACCS)]
            g = GPS[(v['idx'] + cycle) % len(GPS)]
            lat = g[0] + v['offset'] * 0.0003
            lon = g[1] + v['offset'] * 0.0002
            
            # Déterminer le scénario réel selon la température
            scenario = get_scenario(t)
            alert = "⚠️ FIEVRE!" if t > 39.5 else ("🔥 Chaleurs" if scenario == 'heating' else "")
            
            payload = encode(t, a[0], a[1], a[2], lat, lon, g[2])
            ok = envoyer_ttn(v['device'], payload)
            
            print(f"  {'✅' if ok else '❌'} {v['id']} | {t:.1f}°C | {scenario} {alert}")
            
            all_data.append({
                "id": v['id'],
                "temp": round(float(t), 1),
                "ax": round(float(a[0]), 2),
                "ay": round(float(a[1]), 2),
                "az": round(float(a[2]), 2),
                "lat": round(float(lat), 4),
                "lon": round(float(lon), 4),
                "scenario": scenario,
                "state": "fv" if t > 39.5 else ("ht" if scenario == 'heating' else "ok")
            })
        
        with open('data.json', 'w') as f:
            json.dump(all_data, f)
        
        print(f"  ── Cycle {cycle} | Dashboard: http://localhost:5000")
        time.sleep(10)

except KeyboardInterrupt:
    print("\n✅ Arrêté.")