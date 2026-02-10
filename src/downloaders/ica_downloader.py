# =============================================================================
# SCRIPT PER DESCARREGAR DADES ICA (ÍNDEX DE QUALITAT DE L'AIRE)
# =============================================================================

# Importar les biblioteques necessàries
import requests, time, datetime, urllib3  # Per fer peticions HTTP, gestionar temps i dates, i ignorar warnings SSL
from pathlib import Path  # Per gestionar camins d'arxius de manera segura

# Desactivar els warnings d'SSL per evitar missatges d'avís en descàrregues sense verificació
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Definir el directori de sortida per les dades descarregades
out_dir = Path("data/raw/ica/")
# Crear el directori si no existeix, incloent els pares si cal
out_dir.mkdir(parents=True, exist_ok=True)

# Calcular el temps final: 24 hores des d'ara
end_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)

# Bucle principal: continuar mentre no s'hagi arribat al temps final
while datetime.datetime.now(datetime.UTC) < end_time:
    # Obtenir l'hora actual en UTC
    now = datetime.datetime.now(datetime.UTC)
    # Crear el nom de l'arxiu basat en la data i hora actual
    filename = out_dir / f"ica_{now:%Y-%m-%dT%H}.csv"
    # URL de l'API per obtenir les dades ICA
    url = "https://ica.miteco.es/datos/ica-ultima-hora.csv"

    # Mostrar missatge de descàrrega
    print(f"Descarregant {filename.name} ...")
    try:
        # Fer la petició GET a l'URL sense verificar el certificat SSL, amb timeout de 30 segons
        r = requests.get(url, verify=False, timeout=30)
        # Comprovar si la resposta és correcta (codi 200)
        if r.status_code == 200:
            # Obrir l'arxiu en mode binari i escriure el contingut de la resposta
            with open(filename, "wb") as f:
                f.write(r.content)
            # Confirmar que les dades s'han guardat
            print("Dades guardades correctament.")
        else:
            # Mostrar error si el codi de resposta no és 200
            print(f"Error en la descàrrega: {r.status_code}")
    except Exception as e:
        # Capturar i mostrar qualsevol error inesperat
        print(f"Error inesperat: {e}")

    # Esperar fins a la següent hora exacta (3600 segons = 1 hora)
    print("Esperant 1 hora per a la següent descàrrega...\n")
    time.sleep(3600)

# Missatge final quan es completa la recollida
print("Recollida de dades completada!")
