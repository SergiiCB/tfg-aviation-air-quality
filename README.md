# Anàlisi de Correlació entre Densitat de Trànsit Aeri i Qualitat de l'Aire a Espanya
*Grau de Ciència de Dades Aplicada / Applied Data Science - Universitat Oberta de Catalunya (UOC)*

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/license/mit)
 
### 🔬📋Descripció del Projecte

Aquest Treball Final de Grau (TFG) analitza la possible correlació entre la **densitat de trànsit aeri** i la **qualitat de l'aire** a Espanya. L'estudi utilitza dades en temps real de:

- [🔗](https://www.adsbexchange.com/version-2-api-wip/)**ADS-B Exchange API**: Dades de posició, altitud i velocitat d'aeronaus.
- [🔗](https://ica.miteco.es/)**ICA (Índex de Qualitat de l'Aire) - MITECO**: Mesures horàries de qualitat de l'aire.

### 🎯 Objectius

1. Recopilar dades de trànsit aeri i qualitat de l'aire durant 24 hores.
2. Processar i netejar les dades per a l'anàlisi.
3. Analitzar la correlació espacial i temporal entre ambdues variables.
4. Generar visualitzacions interactives dels resultats.
5. Extreure conclusions sobre la relació entre trànsit aeri i contaminació atmosfèrica.

---

## 📁 Estructura del Projecte

```
tfg-aviation-air-quality/
├── .github/
│   └── workflows
├── src/
│   ├── __init__.py
│   ├── downloaders/
│   │   ├── __init__.py
│   │   ├── adsb_downloader.py
│   │   └── ica_downloader.py
│   ├── processors/
│   │   ├── __init__.py
│   │   └── ica_merger.py
│   └── test/
│       ├── __init__.py
│       └── test_timing_miteco.py
├── logs/
│   ├── downloaders/
│   │   ├── adsb/
│   │   │   └── adsb_downloader.log
│   │   └── ica/
│   │       └── ica_downloader.log
│   └── test/
│       └── timing_analysis.log
├── data/
│   ├── raw/
│   │   ├── adsb/
│   │   │   └── adsb_raw.csv
│   │   └── ica/
│   │       ├── ica_2026-02-23T08.csv
│   │       └── etc.
│   ├── merged/
│   │   └── ica_merged_raw.csv
│   └── processed/
│       ├── adsb/
│       │   └── adsb_clean.csv
│       └── ica/
│           └── ica_clean.csv
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_cleaning_preprocessing.ipynb
│   ├── 03_correlation_analysis.ipynb
│   └── 04_interactive_map.ipynb
├── outputs/
│   ├── maps/
│   │   └── interactive_map.html
│   └── figures/
│       ├── correlation_analysis.png
│       └── etc.
├── .dockerignore
├── .gitignore
├── .env
├── docker-compose.yml
├── Dockerfile
├── index.html
├── README.md
├── requirements.txt
└── LICENSE
```

---

## ⚙️ Instal·lació i Ús

### Opció 1: Amb Docker (Recomanat)

**Requisits:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instal·lat.
- 4GB RAM lliures.
- 2GB espai disc.

**Passos:**

```bash
# 1. Clonar el repositori
git clone https://github.com/SergiiCB/tfg-aviation-air-quality.git
cd tfg-aviation-air-quality

# 2. Iniciar el projecte amb Docker Compose
docker-compose up -d

# 3. Accedir a Jupyter Lab
Obre el navegador a: http://localhost:8888
```

**Comandes útils:**

```bash
# Veure logs del container
docker-compose logs -f

# Aturar el projecte
docker-compose down

# Reconstruir després de canvis
docker-compose up -d --build

# Executar scripts Python dins del container
docker-compose exec tfg-jupyter python src/downloaders/adsb_downloader.py
```

---

### Opció 2: Instal·lació Local (sense Docker)

**Requisits:**
- Python 3.11+
- pip

**Passos:**

```bash
# 1. Clonar el repositori
git clone https://github.com/SergiiCB/tfg-aviation-air-quality.git
cd tfg-aviation-air-quality

# 2. Crear entorn virtual
python -m venv venv

# 3. Activar entorn virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instal·lar dependències
pip install -r requirements.txt

# 5. Iniciar Jupyter Lab
jupyter lab
```

---

## ✈️ Pipeline de Dades

### 1. Recol·lecció de Dades

```bash
# Descarregar dades ADS-B (24h, captura cada 5 min)
python src/downloaders/adsb_downloader.py

# Descarregar dades ICA (24h, captura cada hora)
python src/downloaders/ica_downloader.py
```

### 2. Processament

```bash
# Fusionar tots els fitxers ICA en un sol CSV
python src/processors/ica_merger.py
```

### 3. Anàlisi

Obrir i executar els notebooks en ordre:

1. `01_exploratory_analysis.ipynb` - Exploració inicial de les dades.
2. `02_cleaning_preprocessing.ipynb` - Neteja i preprocessament.
3. `03_correlation_analysis.ipynb` - Anàlisi de correlació.
4. `04_interactive_map.ipynb` - Generació del mapa interactiu.

---

## 🤖 Tecnologies Utilitzades

### Llenguatges i Frameworks
- **Python 3.11**: Llenguatge principal.
- **Jupyter Lab**: Entorn d'anàlisi interactiu.
- **Docker**: Contenidorització i reproducibilitat.

### Llibreries Principals
- **pandas**: Manipulació de dades tabulars.
- **NumPy**: Càlculs numèrics.
- **matplotlib / seaborn**: Visualització estàtica.
- **folium**: Mapes interactius.
- **scipy / scikit-learn**: Anàlisi estadística i correlacions.
- **requests**: Peticions a APIs.

---

## 📈 Resultats i Conclusions

L'anàlisi s'ha consolidat com una **Prova de Concepte (PoC)** metodològica. Tot i la limitació temporal del dataset (24 hores) a causa de la indisponibilitat del servidor extern del MITECO per obtenir un conjunt de dades més gran, s'ha validat amb èxit tota la pipeline de dades, des de la ingesta automatitzada fins a la visualització geoespacial.

### 1. Anàlisi Estadística
S'ha realitzat un encreuament espai-temporal d'alta precisió alineant els vols amb les **estacions de fons (background)** per minimitzar el soroll del trànsit rodat.

| Mètrica | Valor | Interpretació |
| :--- | :--- | :--- |
| **Observacions vinculades** | 603 | Registres amb coincidència en malla (0.1º) i hora. |
| **Coeficient de Pearson ($r$)** | `-0.013` | Absència de correlació lineal. |
| **Coeficient de Spearman ($\rho$)** | `-0.097` | Relació monòtona molt baixa ($p = 0.018$). |
| **Coeficient de Determinació ($R^2$)** | `0.0002` | El trànsit explica el 0.02% de la variància de l'ICA. |

**Conclusió científica:** Els resultats són coherents amb la física de la dispersió atmosfèrica (especialment sota la limitació de 24 hores). Les emissions a altituds de creuer es dispersen en grans volums d'aire, fent que el seu impacte immediat a nivell de superfície sigui indetectable en una finestra temporal curta sense l'aplicació de models de dispersió complexos.

### 2. Visualització Interactiva
S'ha desenvolupat un entorn cartogràfic dinàmic que integra les dues fonts de dades:

* **Capes de Densitat**: Representació de l'activitat aèria sobre una malla geoespacial.
* **Estacions ICA**: Marcadors interactius amb codi de colors oficial i pop-ups personalitzats (HTML/CSS) amb el detall de cada contaminant.
* **Accés directe**: 🌐 **[Veure Mapa Interactiu](https://sergiicb.github.io/tfg-aviation-air-quality/outputs/maps/interactive_map.html)**

---

## 🔐 Configuració d'API Keys
> .[!IMPORTANT].
> No pugis mai les teves **API keys** al repositori!

Crea un fitxer `.env` a l'arrel del projecte:

```bash
# .env (aquest fitxer està ignorat per Git)
ADSB_API_KEY="la-teva-api-key-aqui"
```

---

## Agraïments

- **ADS-B Exchange**: Per proporcionar dades de trànsit aeri en temps real.
- **MITECO (Ministerio para la Transición Ecológica)**: Per les dades d'ICA.
- **Tutora del TFG**: Per la supervisió i guia del projecte.

---

## 👤 Sergi Cózar Badia
 
Treball Final de Grau - Universitat Oberta de Catalunya (UOC)

Grau de Ciència de Dades Aplicada / Applied Data Science

Curs 2025-2026

---

## 📧 Contacte

Per a preguntes o col·laboracions:
- Email: [sergicozar@gmail.com]
- GitHub: [@SergiiCB](https://github.com/SergiiCB)

---

## 📄 Llicència

El codi font d'aquest projecte està sota la [llicència MIT](https://opensource.org). No obstant això, la memòria del TFG i la documentació tècnica associada estan subjectes a la llicència Reconocimiento-NoComercial-SinObraDerivada [3.0 España de Creative Commons](http://creativecommons.org/licenses/by-nc-nd/3.0/es/)

Consulta el fitxer [LICENSE](/LICENSE) per més detalls.

---
