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

# =============================================================================
# PARÀMETRES DE RECOLLIDA (CONFIGURACIÓ TFG)
# =============================================================================

DURADA_DIES = 7 # Durada total de la recollida (7 dies)
INTERVAL_MINUTS = 5 # Interval entre captures (5 minuts)

# Càlculs automàtics
CAPTURES_PER_HORA = 60 // INTERVAL_MINUTS
CAPTURES_PER_DIA = 24 * CAPTURES_PER_HORA
N = DURADA_DIES * CAPTURES_PER_DIA  # Total de captures
SLEEP = INTERVAL_MINUTS * 60  # Segons entre captures

# Directori de sortida
OUTPUT_DIR = Path("data/raw/adsb/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "adsb_raw.csv"

# =============================================================================
# INICIALITZACIÓ
# =============================================================================

print("=" * 70)
print("RECOLLIDA DE DADES ADS-B")
print("=" * 70)
print(f"Durada: {DURADA_DIES} dies")
print(f"Interval: {INTERVAL_MINUTS} minuts ({CAPTURES_PER_HORA} captures/hora)")
print(f"Total captures: {N:,}")
print(f"Registres esperats: ~{N * 477:,} (estimació basada en mitjana)")
print(f"Fitxer sortida: {OUTPUT_FILE}")
print("=" * 70)
print()

# Crear l'arxiu CSV amb les capçaleres
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields)

# Inicialitzar variables per comptar estadístiques
temps_inici = datetime.utcnow()
total_avions = 0
captures_exitoses = 0
captures_error = 0

print(f"Inici: {temps_inici.isoformat()} UTC")
print()

# =============================================================================
# BUCLE PRINCIPAL
# =============================================================================

for i in range(N):
    temps_captura_inici = datetime.utcnow()
    
    try:
        # Realitzar la sol·licitud a l'API
        r = requests.get(URL, headers=headers, timeout=30)
        
        if r.status_code != 200:
            print(f"[{temps_captura_inici:%H:%M:%S}] Error {r.status_code} en captura {i+1}/{N}")
            captures_error += 1
            time.sleep(60)  # Esperar 1 minut abans de reintentar
            continue
        
        # Obtindre les dades de la resposta
        data = r.json()
        avions = data.get("ac", [])
        ts = temps_captura_inici.isoformat()
        
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
        
        print(f"[{temps_captura_inici:%H:%M:%S}] ✓ Captura {i+1}/{N}: {len(avions)} avions")
        
        # Estadístiques cada hora
        if (i + 1) % CAPTURES_PER_HORA == 0:
            hores = (i + 1) // CAPTURES_PER_HORA
            temps_transcorregut = (datetime.utcnow() - temps_inici).total_seconds() / 3600
            taxa_exit = (captures_exitoses / (captures_exitoses + captures_error) * 100) if (captures_exitoses + captures_error) > 0 else 0
            mitjana_avions = total_avions / captures_exitoses if captures_exitoses > 0 else 0
            
            print()
            print(f"Estadístiques després de {hores}h ({temps_transcorregut:.1f}h reals)")
            print(f"Captures exitoses: {captures_exitoses} | Errors: {captures_error} | Taxa èxit: {taxa_exit:.1f}%")
            print(f"Total avions: {total_avions:,} | Mitjana: {mitjana_avions:.1f} avions/captura")
            print(f"Projecció 7 dies: {int(mitjana_avions * N):,} avions")
            print()
        
    except Exception as e:
        print(f"[{temps_captura_inici:%H:%M:%S}] Error captura {i+1}/{N}: {e}")
        captures_error += 1
        time.sleep(60)
        continue
    
    # Esperar següent captura (només si no és l'última)
    if i < N - 1:
        # Calcular temps d'espera ajustat per compensar el temps de processament
        temps_captura_fi = datetime.utcnow()
        temps_processat = (temps_captura_fi - temps_captura_inici).total_seconds()
        temps_espera_ajustat = max(0, SLEEP - temps_processat)
        
        if temps_espera_ajustat > 0:
            time.sleep(temps_espera_ajustat)

# =============================================================================
# RESUM FINAL
# =============================================================================

temps_final = datetime.utcnow()
temps_total_hores = (temps_final - temps_inici).total_seconds() / 3600
mitjana_final = total_avions / max(captures_exitoses, 1)

print()
print("=" * 70)
print("RECOL·LECCIÓ COMPLETADA")
print("=" * 70)
print(f"Temps total: {temps_total_hores:.1f} hores ({DURADA_DIES} dies)")
print(f"Captures: {captures_exitoses}/{N} exitoses | {captures_error} errors")
print(f"Taxa d'èxit: {(captures_exitoses/(captures_exitoses+captures_error)*100):.1f}%")
print(f"Total avions: {total_avions:,} registres")
print(f"Mitjana: {mitjana_final:.1f} avions per captura")
print(f"Fitxer: {OUTPUT_FILE}")
print(f"Mida aproximada: {OUTPUT_FILE.stat().st_size / (1024**2):.1f} MB")
print("=" * 70)