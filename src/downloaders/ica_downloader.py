# =============================================================================
# SCRIPT PER DESCARREGAR DADES ICA (ÍNDEX DE QUALITAT DE L'AIRE)
# =============================================================================

# Importar les biblioteques necessàries
import requests, time, datetime, urllib3
from pathlib import Path

# Desactivar els warnings d'SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =============================================================================
# CONFIGURACIÓ
# =============================================================================

# Durada de la recollida
DURADA_DIES = 7  # 1 setmana

# MITECO publica les dades entre els minuts 06 i 07 de cada hora
MINUT_DESCARREGA = 10

# Sistema de reintents
MAX_INTENTS = 3        # Intents màxims per descàrrega
ESPERA_REINTENT = 120  # Segons entre reintents (2 minuts)

# Directori de sortida
OUT_DIR = Path("data/raw/ica/")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# URL de l'API
URL = "https://ica.miteco.es/datos/ica-ultima-hora.csv"

# =============================================================================
# INICIALITZACIÓ
# =============================================================================

print("=" * 70)
print("RECOLLIDA DE DADES ICA")
print("=" * 70)
print(f"Durada: {DURADA_DIES} dies ({DURADA_DIES * 24} hores)")
print(f"Descàrrega: cada hora al minut {MINUT_DESCARREGA}")
print(f"Reintents: {MAX_INTENTS} intents màxims amb {ESPERA_REINTENT}s entre intents")
print(f"Directori: {OUT_DIR.absolute()}")
print(f"Fitxers esperats: {DURADA_DIES * 24}")
print("=" * 70)
print()

# Calcular temps final
end_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=DURADA_DIES)
temps_inici = datetime.datetime.now(datetime.UTC)

print(f"Inici: {temps_inici:%Y-%m-%d %H:%M:%S} UTC")
print(f"Final previst: {end_time:%Y-%m-%d %H:%M:%S} UTC")
print()

# Comptadors d'estadístiques
descarregues_exitoses = 0
descarregues_error = 0
total_intents = 0

# =============================================================================
# BUCLE PRINCIPAL
# =============================================================================

while datetime.datetime.now(datetime.UTC) < end_time:
    # Obtenir l'hora actual en UTC
    now = datetime.datetime.now(datetime.UTC)
    
    # =========================================================================
    # NOM D'ARXIU AMB HORA DE LES DADES (no hora de descàrrega)
    # =========================================================================
    # Les dades descarregades a les 10:10 corresponen a 09:00-10:00, restem 1 hora al nom de l'arxiu
    hora_dades = now - datetime.timedelta(hours=1)
    filename = OUT_DIR / f"ica_{hora_dades:%Y-%m-%dT%H}.csv"

    # Mostrar missatge de descàrrega
    print(f"[{now:%Y-%m-%d %H:%M:%S}] Descarregant dades de {hora_dades:%H}:00-{now:%H}:00...")
    
    # =========================================================================
    # SISTEMA DE REINTENTS
    # =========================================================================
    descarregat = False
    
    for intent in range(1, MAX_INTENTS + 1):
        total_intents += 1
        
        try:
            # Fer la petició GET a l'URL
            r = requests.get(URL, verify=False, timeout=60)
            
            # Comprovar si la resposta és correcta i que no estigui buit
            if r.status_code == 200 and len(r.content) > 200:
                # Obrir l'arxiu en mode binari i escriure el contingut
                with open(filename, "wb") as f:
                    f.write(r.content)
                
                # Confirmar descàrrega exitosa
                descarregues_exitoses += 1
                descarregat = True
                
                if intent == 1:
                    print(f"Guardat: {filename.name} ({len(r.content)} bytes)")
                else:
                    print(f"Guardat al intent {intent}/{MAX_INTENTS}: {filename.name} ({len(r.content)} bytes)")
                
                break  # Sortir del bucle de reintents
                
            else:
                # Error HTTP o fitxer buit
                if intent < MAX_INTENTS:
                    print(f"⚠ Intent {intent}/{MAX_INTENTS}: Error HTTP {r.status_code} o fitxer buit. Reintentant en {ESPERA_REINTENT}s...")
                    time.sleep(ESPERA_REINTENT)
                else:
                    print(f"Error final després de {MAX_INTENTS} intents: HTTP {r.status_code}")
                    descarregues_error += 1
                    
        except requests.Timeout:
            # Timeout en la connexió
            if intent < MAX_INTENTS:
                print(f"⚠ Intent {intent}/{MAX_INTENTS}: Timeout. Reintentant en {ESPERA_REINTENT}s...")
                time.sleep(ESPERA_REINTENT)
            else:
                print(f"Error final després de {MAX_INTENTS} intents: Timeout")
                descarregues_error += 1
                
        except Exception as e:
            # Altres errors
            if intent < MAX_INTENTS:
                print(f"⚠ Intent {intent}/{MAX_INTENTS}: {type(e).__name__}: {e}. Reintentant en {ESPERA_REINTENT}s...")
                time.sleep(ESPERA_REINTENT)
            else:
                print(f"Error final després de {MAX_INTENTS} intents: {type(e).__name__}: {e}")
                descarregues_error += 1

    # =========================================================================
    # ESTADÍSTIQUES PERIÒDIQUES
    # =========================================================================
    hores_transcorregudes = (now - temps_inici).total_seconds() / 3600
    
    if descarregues_exitoses > 0 and descarregues_exitoses % 6 == 0:
        taxa_exit = (descarregues_exitoses / (descarregues_exitoses + descarregues_error) * 100) if (descarregues_exitoses + descarregues_error) > 0 else 0
        mitjana_intents = total_intents / (descarregues_exitoses + descarregues_error)
        
        print()
        print(f"Estadístiques després de {hores_transcorregudes:.1f}h")
        print(f"Descàrregues: {descarregues_exitoses} exitoses | {descarregues_error} errors")
        print(f"Taxa d'èxit: {taxa_exit:.1f}%")
        print(f"Mitjana d'intents per descàrrega: {mitjana_intents:.2f}")
        print()

    # =========================================================================
    # CÀLCUL D'ESPERA SINCRONITZADA
    # =========================================================================
    now = datetime.datetime.now(datetime.UTC)
    proxima_descarrega = now.replace(minute=MINUT_DESCARREGA, second=0, microsecond=0)
    
    # Si ja hem passat el minut de descàrrega, passar a la següent hora
    if proxima_descarrega <= now:
        proxima_descarrega += datetime.timedelta(hours=1)
    
    segons_espera = (proxima_descarrega - now).total_seconds()
    minuts_espera = int(segons_espera / 60)
    
    # Només esperar si encara no hem arribat al final
    if datetime.datetime.now(datetime.UTC) < end_time:
        print(f"Esperant {minuts_espera} min fins a {proxima_descarrega:%H:%M} UTC...\n")
        time.sleep(segons_espera)

# =============================================================================
# RESUM FINAL
# =============================================================================

temps_final = datetime.datetime.now(datetime.UTC)
temps_total_hores = (temps_final - temps_inici).total_seconds() / 3600
taxa_exit_final = (descarregues_exitoses / (descarregues_exitoses + descarregues_error) * 100) if (descarregues_exitoses + descarregues_error) > 0 else 0
mitjana_intents_final = total_intents / (descarregues_exitoses + descarregues_error) if (descarregues_exitoses + descarregues_error) > 0 else 0

print()
print("=" * 70)
print("RECOLLIDA DE DADES COMPLETADA")
print("=" * 70)
print(f"Temps total: {temps_total_hores:.1f} hores ({DURADA_DIES} dies)")
print(f"Descàrregues exitoses: {descarregues_exitoses}/{DURADA_DIES * 24}")
print(f"Errors: {descarregues_error}")
print(f"Taxa d'èxit: {taxa_exit_final:.1f}%")
print(f"Total intents realitzats: {total_intents}")
print(f"Mitjana d'intents per descàrrega: {mitjana_intents_final:.2f}")
print(f"Directori: {OUT_DIR.absolute()}")
print()

# Verificar fitxers generats
fitxers_generats = sorted(OUT_DIR.glob("ica_*.csv"))
print(f"Fitxers generats: {len(fitxers_generats)}")
if fitxers_generats:
    print(f"Primer fitxer: {fitxers_generats[0].name}")
    print(f"Últim fitxer: {fitxers_generats[-1].name}")

print("=" * 70)