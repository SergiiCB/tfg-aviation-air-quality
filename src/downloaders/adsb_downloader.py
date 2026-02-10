# =============================================================================
# SCRIPT PER DESCARREGAR DADES AMB L'API D'ADS-B EXCHANGE
# =============================================================================

# Importar les biblioteques necessàries
import requests
import csv
import time
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# =============================================================================
# CONFIGURACIÓ
# =============================================================================

# Carregar variables d'entorn des del fitxer .env
load_dotenv()

# Llegir l'API key des de les variables d'entorn
API_KEY = os.getenv("ADSB_API_KEY")

# Verificar que l'API key s'ha carregat correctament
if not API_KEY:
    raise ValueError(
        "ERROR: No s'ha trobat l'API key!\n"
        "Crea un fitxer .env a l'arrel del projecte amb:\n"
        "ADSB_API_KEY=la-teva-api-key-aqui"
    )

# Configuració de l'API
URL = "https://aircraftscatter.p.rapidapi.com/lat/40.4/lon/-3.7/"

# Capçaleres per les sol·licituds
headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "aircraftscatter.p.rapidapi.com"
}

# Camps a recollir
fields = [
    "hex", "r", "t", "flight", "lat", "lon", "alt_baro", "alt_geom",
    "gs", "track", "type", "category", "timestamp"
]

# Paràmetres de la recollida de dades
N = 288        # 24 hores amb captures cada 5 minuts
SLEEP = 300    # 5 minuts = 300 segons
OUTPUT_FILE = Path("data/raw/adsb/adsb_raw.csv")

# =============================================================================
# INICIALITZACIÓ
# =============================================================================

print(f"Iniciant recollida: {N} captures cada {SLEEP//60} min → {OUTPUT_FILE}")

# Crear l'arxiu CSV amb les capçaleres
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields)

# Inicialitzar variables per comptar estadístiques de la recollida
total_avions = 0  # Nombre total d'avions detectats en totes les captures
captures_exitoses = 0  # Nombre de captures que s'han realitzat correctament
captures_error = 0  # Nombre de captures que han fallat

# =============================================================================
# BUCLE PRINCIPAL
# =============================================================================

for i in range(N):
    try:
        # Realitzar la sol·licitud a l'API
        r = requests.get(URL, headers=headers, timeout=30)
        
        if r.status_code != 200:
            print(f"Error {r.status_code} en captura {i+1}/{N}")
            captures_error += 1
            time.sleep(60)
            continue
        
        # Obtindre les dades de la resposta
        data = r.json()
        avions = data.get("ac", [])
        ts = datetime.utcnow().isoformat()
        
        # Escriure les dades a l'arxiu CSV
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for a in avions:
                row = [
                    a.get("hex"),
                    a.get("r"),
                    a.get("t"),
                    a.get("flight", "").strip() or a.get("call", "").strip(),
                    a.get("lat"),
                    a.get("lon"),
                    a.get("alt_baro"),
                    a.get("alt_geom"),
                    a.get("gs"),
                    a.get("track"),
                    a.get("type"),
                    a.get("category"),
                    ts
                ]
                writer.writerow(row)
        
        # Actualitzar estadístiques
        captures_exitoses += 1
        total_avions += len(avions)
        
        print(f"Captura {i+1}/{N}: {len(avions)} avions")
        
        # Estadístiques cada hora
        if (i + 1) % 12 == 0:
            print(f"\n--- Estadístiques després de {(i+1)//12}h ---")
            print(f"Captures exitoses: {captures_exitoses} | Errors: {captures_error}")
            print(f"Total avions: {total_avions} | Mitjana: {total_avions/captures_exitoses:.1f}\n")
        
    except Exception as e:
        print(f"Error captura {i+1}/{N}: {e}")
        captures_error += 1
        time.sleep(60)
        continue
    
    # Esperar següent captura
    if i < N - 1:
        time.sleep(SLEEP)

# =============================================================================
# RESUM FINAL
# =============================================================================

print("\n" + "="*60)
print("RECOL·LECCIÓ COMPLETADA")
print(f"Captures: {captures_exitoses}/{N} | Errors: {captures_error}")
print(f"Total avions: {total_avions:,} | Mitjana: {total_avions/max(captures_exitoses, 1):.1f}")
print(f"Fitxer: {OUTPUT_FILE}")
print("="*60)
