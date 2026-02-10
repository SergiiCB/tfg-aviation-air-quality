# =============================================================================
# DOCKERFILE
# =============================================================================

# Imatge base: Python 3.11
FROM python:3.11-slim

# Informació del mantenidor
LABEL maintainer="TFG Aviation Air Quality"
LABEL description="Docker environment for aviation traffic and air quality correlation analysis"

# Establir el directori de treball dins el container
WORKDIR /tfg

# Instal·lar dependències del sistema necessàries
# - curl: per descàrregues
# - build-essential: compiladors per algunes llibreries Python
# - git: control de versions
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primer (per aprofitar el cache de Docker)
COPY requirements.txt .

# Instal·lar les dependències Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar tot el codi del projecte
COPY . .

# Crear les carpetes necessàries si no existeixen
RUN mkdir -p data/raw/adsb data/raw/ica data/merged data/processed/adsb data/processed/ica outputs/maps outputs/figures

# Exposar el port de Jupyter
EXPOSE 8888

# Configurar Jupyter per acceptar connexions externes
ENV JUPYTER_ENABLE_LAB=yes

# Comanda per defecte: iniciar Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]