FROM python:3.10-slim

# Imposta le variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    NUMBA_CACHE_DIR=/tmp \
    NUMBA_DISABLE_JIT=1 \
    PYMATTING_DISABLE_NUMBA=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers \
    HF_DATASETS_CACHE=/app/.cache/huggingface/datasets \
    TORCH_HOME=/app/.cache/torch

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

# Installa git (necessario per alcuni modelli HuggingFace)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copia i file dei requirements
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Crea directory per le immagini temporanee e cache
RUN mkdir -p /app/temp_images \
    && mkdir -p /app/.cache/huggingface/transformers \
    && mkdir -p /app/.cache/huggingface/datasets \
    && mkdir -p /app/.cache/torch

# Copia il codice dell'applicazione
COPY main.py .
COPY image_processor.py .

# Crea un utente non-root per sicurezza
RUN groupadd -r appuser && useradd -r -g appuser appuser -m
RUN chown -R appuser:appuser /app
RUN mkdir -p /home/appuser/.u2net && chown -R appuser:appuser /home/appuser

# Pre-download dei modelli (opzionale, se HF_TOKEN è fornito)
# Questo step viene eseguito come root per evitare problemi di permessi
ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}

# Script per pre-scaricare i modelli se il token è fornito
RUN if [ -n "$HF_TOKEN" ]; then \
        echo "Token HF fornito, pre-download dei modelli..." && \
        python -c "import os; os.environ['HF_TOKEN']='$HF_TOKEN'; \
        from transformers import AutoModelForImageSegmentation; \
        try: \
            model = AutoModelForImageSegmentation.from_pretrained('briaai/RMBG-2.0', trust_remote_code=True); \
            print('✅ RMBG-2.0 scaricato con successo'); \
        except Exception as e: \
            print(f'⚠️  RMBG-2.0 non disponibile: {e}'); \
            try: \
                model = AutoModelForImageSegmentation.from_pretrained('briaai/RMBG-1.4', trust_remote_code=True); \
                print('✅ RMBG-1.4 scaricato come fallback'); \
            except Exception as e2: \
                print(f'⚠️  Nessun modello RMBG disponibile: {e2}'); \
        "; \
    else \
        echo "Nessun token HF fornito, modelli verranno scaricati al primo avvio"; \
    fi

USER appuser

# Espone la porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando di avvio
CMD ["python", "main.py"]