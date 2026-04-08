# =============================================================================
# TEST PER DESCOBRIR QUAN MITECO PUBLICA LES DADES
# =============================================================================

# Sscript de descarrega cada 5 minuts, per detectar quan canvien les dades


import requests
import time
import datetime
import urllib3
from pathlib import Path
import hashlib

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://ica.miteco.es/datos/ica-ultima-hora.csv"
LOG_FILE = Path("logs/test/timing_analysis.log")


def obtenir_hash(contingut):
    # Calcula hash MD5 del contingut.
    return hashlib.md5(contingut).hexdigest()


def obtenir_primera_linia(contingut):
    #Extreu la primera línia de dades (no capçalera) per identificar l'hora
    try:
        linies = contingut.decode('utf-8', errors='ignore').split('\n')
        # Retornem les primeres 3 línies per veure capçalera + dades
        return '\n'.join(linies[:3])
    except:
        return "Error llegint contingut"


def descarregar_i_analitzar():
    # Descarrega les dades i retorna hash + mostra de contingut.
    try:
        r = requests.get(URL, verify=False, timeout=30)
        if r.status_code == 200 and len(r.content) > 200:
            hash_actual = obtenir_hash(r.content)
            mostra = obtenir_primera_linia(r.content)
            return hash_actual, mostra, len(r.content)
        else:
            return None, None, 0
    except Exception as e:
        return None, None, 0


def registrar_log(missatge):
    # Guarda al fitxer de log i mostra per pantalla.
    now = datetime.datetime.now(datetime.UTC)
    linia = f"[{now:%Y-%m-%d %H:%M:%S}] {missatge}"
    print(linia)
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(linia + "\n")


def main():
    # Descarrega cada 5 minuts durant 24 hores i detecta quan canvien les dades.
    print("=" * 80)
    print("TEST DE TIMING - ANÀLISI DE PUBLICACIÓ DE DADES ICA")
    print("=" * 80)
    print(f"Aquest script descarregarà cada 5 minuts durant 24 hores")
    print(f"per determinar EXACTAMENT quan el MITECO publica les dades noves.")
    print()
    print(f"Log: {LOG_FILE.absolute()}")
    print("=" * 80)
    print()

    # Inicialitzar log
    registrar_log("=" * 80)
    registrar_log("INICI DEL TEST DE TIMING")
    registrar_log("=" * 80)

    temps_final = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
    hash_anterior = None
    hora_anterior = None
    comptador = 0

    while datetime.datetime.now(datetime.UTC) < temps_final:
        now = datetime.datetime.now(datetime.UTC)
        hora_actual = now.hour

        # Descarregar dades
        hash_actual, mostra, mida = descarregar_i_analitzar()

        if hash_actual is None:
            registrar_log(f"Error en la descàrrega (minut {now.minute})")
        else:
            # Detectar si ha canviat el contingut
            if hash_actual != hash_anterior:
                if hash_anterior is not None:
                    # DADES NOVES DETECTADES!
                    registrar_log("")
                    registrar_log(f"CANVI DETECTAT! Hora: {now.hour:02d}:{now.minute:02d}")
                    registrar_log(f"Hash anterior: {hash_anterior[:16]}...")
                    registrar_log(f"Hash nou: {hash_actual[:16]}...")
                    registrar_log(f"Mida: {mida} bytes")
                    registrar_log(f"Mostra de dades:")
                    for linia in mostra.split('\n'):
                        registrar_log(f"{linia[:70]}")
                    registrar_log("")
                else:
                    # Primera descàrrega
                    registrar_log(f"Primera descàrrega - Minut {now.minute:02d}")
                    registrar_log(f"Hash: {hash_actual[:16]}...")
                    registrar_log(f"Mida: {mida} bytes")

                hash_anterior = hash_actual
                hora_anterior = hora_actual
            else:
                # Dades iguals
                registrar_log(f"Minut {now.minute:02d} - Sense canvis (Hash: {hash_actual[:8]}...)")

        comptador += 1

        # Esperar 5 minuts
        proxima_execucio = now + datetime.timedelta(minutes=5)
        proxima_execucio = proxima_execucio.replace(second=0, microsecond=0)

        segons_espera = (proxima_execucio - datetime.datetime.now(datetime.UTC)).total_seconds()
        if segons_espera > 0:
            time.sleep(segons_espera)

    # Resum final
    registrar_log("")
    registrar_log("=" * 80)
    registrar_log("TEST COMPLETAT")
    registrar_log(f"Total de descàrregues: {comptador}")
    registrar_log("Revisa el log per veure els patrons de publicació")
    registrar_log("=" * 80)

    print()
    print("Test completat!")
    print(f"Revisa el fitxer {LOG_FILE} per veure l'anàlisi completa")


if __name__ == "__main__":
    main()