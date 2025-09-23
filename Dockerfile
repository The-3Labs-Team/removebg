FROM python:3.11-slim

# Imposta le variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    NUMBA_CACHE_DIR=/tmp \
    NUMBA_DISABLE_JIT=1 \
    PYMATTING_DISABLE_NUMBA=1

# Installa le dipendenze di sistema necessarie per rembg
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia i file dei requirements
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Crea directory per le immagini temporanee
RUN mkdir -p /app/temp_images

# Copia il codice dell'applicazione
COPY main.py .
COPY image_processor.py .

# Crea un utente non-root per sicurezza
RUN groupadd -r appuser && useradd -r -g appuser appuser -m
RUN chown -R appuser:appuser /app
RUN mkdir -p /home/appuser/.u2net && chown -R appuser:appuser /home/appuser
USER appuser

# Espone la porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando di avvio
CMD ["python", "main.py"]