# =============================================================================
# SCRIPT PER FUSIONAR LES DADES ICA (ÍNDEX DE QUALITAT DE L'AIRE)
# =============================================================================

# Importar les biblioteques necessàries
import pandas as pd  # Per gestionar i manipular dades en format tabular
from pathlib import Path # Per gestionar camins d'arxius de manera segura i multiplataforma

# =============================================================================
# CONFIGURACIÓ
# =============================================================================

# Definir el directori on es troben els arxius CSV descarregats
input_dir = Path("data/raw/ica")

# Definir l'arxiu de sortida on es guardaran les dades fusionades
output_dir = Path("data/merged")

# Crear el directori de sortida si no existeix
output_dir.mkdir(parents=True, exist_ok=True)

# =============================================================================
# FUSIÓ DE LES DADES
# =============================================================================

# Recórrer tots els arxius CSV del directori d'entrada
all_files = sorted(input_dir.glob("ica_*.csv"))

# Comprovar si s'han trobat arxius
if not all_files:
    raise FileNotFoundError("No s'han trobat fitxers ICA")

# Fusionar tots els DataFrames en un de sol
df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)

# =============================================================================
# GUARDAR LES DADES FUSIONADES
# =============================================================================

# Guardar el DataFrame fusionat
output_file = output_dir / "ica_merged_raw"
df.to_csv(output_file, index=False)

# Mostrar estadístiques finals
print(f"S'han combinat {len(all_files)} fitxers ICA")
print(f"Fitxer creat: {output_file}")
