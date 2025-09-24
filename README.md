# Remove Background API

API HTTP per rimuovere lo sfondo dalle immagini utilizzando la libreria `rembg` con modello **birefnet-general** ottimizzato per foto di prodotti.

## Caratteristiche

- ✅ API HTTP protetta da chiave API
- ✅ Download automatico delle immagini da URL
- ✅ Rimozione dello sfondo usando **RMBG-2.0** (BriaAI) o fallback rembg
- ✅ **Metadata dettagliati** incorporati nell'immagine processata
- ✅ Ottimizzato per foto di prodotti e oggetti
- ✅ **Supporto credenziali HuggingFace** per modelli privati
- ✅ Cache persistente per modelli AI
- ✅ Pulizia automatica dei file temporanei
- ✅ Gestione degli errori completa
- ✅ Logging strutturato con timing di processamento
- ✅ Documentazione API automatica (Swagger/OpenAPI)

## Installazione

1. **Clona o crea la directory del progetto:**
   ```bash
   cd /path/to/your/project
   ```

2. **Installa le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura le variabili d'ambiente:**
   ```bash
   cp .env.example .env
   ```
   
   Modifica il file `.env` con le tue configurazioni:
   ```bash
   API_KEY=your-secret-api-key-here
   HOST=0.0.0.0
   PORT=8000
   DEBUG=false
   
   # Opzionale: Token HuggingFace per modelli migliori
   HF_TOKEN=your-huggingface-token-here
   ```

## Utilizzo

### Avvio del server

```bash
python main.py
```

Il server sarà disponibile su `http://localhost:8000`

### Endpoint disponibili

#### GET /remove-background

Rimuove lo sfondo da un'immagine specificata tramite URL.

**Parametri:**
- `image_url` (query parameter): URL dell'immagine da processare
- `X-API-Key` (header): Chiave API per l'autenticazione

**Esempio di richiesta:**
```bash
curl -X GET "http://localhost:8000/remove-background?image_url=https://example.com/image.jpg" \
     -H "X-API-Key: your-api-key-here" \
     --output result.png
```

#### POST /remove-background

Alternativa POST per URL molto lunghi.

**Esempio di richiesta:**
```bash
curl -X POST "http://localhost:8000/remove-background" \
     -H "X-API-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"image_url": "https://example.com/very-long-url..."}' \
     --output result.png
```

#### Altri endpoint

- `GET /` - Informazioni sull'API
- `GET /health` - Health check
- `GET /docs` - Documentazione Swagger (solo in debug mode)

### Formati supportati

L'API supporta i seguenti formati di immagine:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff)
- WebP (.webp)

### Esempio con Python

```python
import requests

# Configurazione
api_url = "http://localhost:8000/remove-background"
api_key = "your-api-key-here"
image_url = "https://example.com/image.jpg"

# Richiesta
response = requests.get(
    api_url,
    params={"image_url": image_url},
    headers={"X-API-Key": api_key}
)

if response.status_code == 200:
    with open("result.png", "wb") as f:
        f.write(response.content)
    print("Immagine processata con successo!")
else:
    print(f"Errore: {response.status_code} - {response.text}")
```

### Esempio con JavaScript

```javascript
const apiUrl = 'http://localhost:8000/remove-background';
const apiKey = 'your-api-key-here';
const imageUrl = 'https://example.com/image.jpg';

fetch(`${apiUrl}?image_url=${encodeURIComponent(imageUrl)}`, {
    headers: {
        'X-API-Key': apiKey
    }
})
.then(response => {
    if (response.ok) {
        return response.blob();
    }
    throw new Error('Errore nella richiesta');
})
.then(blob => {
    const url = URL.createObjectURL(blob);
    const img = document.createElement('img');
    img.src = url;
    document.body.appendChild(img);
})
.catch(error => console.error('Errore:', error));
```

## Configurazione avanzata

### Variabili d'ambiente

- `API_KEY`: Chiave API per l'autenticazione (obbligatoria)
- `HOST`: Host su cui avviare il server (default: 0.0.0.0)
- `PORT`: Porta su cui avviare il server (default: 8000)
- `DEBUG`: Modalità debug (default: false)
- `TEMP_DIR`: Directory per i file temporanei (opzionale)
- `HF_TOKEN`: Token HuggingFace per accedere ai modelli migliori (opzionale)

### Token HuggingFace

Per ottenere prestazioni migliori, puoi configurare un token HuggingFace:

1. **Registrati su [HuggingFace](https://huggingface.co/)**
2. **Vai alle [impostazioni token](https://huggingface.co/settings/tokens)**
3. **Crea un nuovo token con permessi di lettura**
4. **Aggiungi il token al tuo file `.env`:**
   ```bash
   HF_TOKEN=hf_your_token_here
   ```

**Vantaggi del token HF:**
- Accesso ai modelli **RMBG-2.0** (migliori prestazioni)
- Nessun limite di rate per il download dei modelli
- Accesso a modelli privati e premium

### Metadata delle immagini

Ogni immagine processata include metadata dettagliati incorporati nel file PNG:

**Metadata standard:**
- Titolo e descrizione del processamento
- Software utilizzato e versione API
- Timestamp di processamento
- URL dell'immagine originale

**Metadata tecnici:**
- Modello AI utilizzato (RMBG-2.0 o rembg)
- Dispositivo di processamento (CPU/GPU)
- Tempo di processamento in secondi
- Formato e dimensioni originali
- Informazioni sul canale alpha

**Metadata strutturati JSON:**
```json
{
  "processing": {
    "timestamp": "2024-01-01T12:00:00",
    "model": "RMBG-2.0 (Transformers)",
    "device": "cpu",
    "processing_time_seconds": 2.45,
    "success": true
  },
  "original": {
    "url": "https://example.com/image.jpg",
    "format": "JPEG",
    "width": 1920,
    "height": 1080,
    "file_size_bytes": 234567
  },
  "output": {
    "format": "PNG",
    "has_alpha": true,
    "width": 1920,
    "height": 1080
  }
}
```

**Come leggere i metadata:**
```python
from PIL import Image

# Apri l'immagine processata
img = Image.open('processed_image.png')

# Leggi i metadata
print("Modello utilizzato:", img.text.get('Processing Model'))
print("Tempo di processamento:", img.text.get('Processing Time'))
print("URL originale:", img.text.get('Source URL'))
print("Metadata JSON:", img.text.get('Processing Info JSON'))
```

### Logging

Il sistema include logging strutturato che registra:
- Richieste API ricevute
- Errori di validazione
- Errori di processamento
- Informazioni di debug (in modalità debug)

### Sicurezza

- Autenticazione tramite API Key
- Validazione degli URL delle immagini
- Verifica del content-type delle immagini
- Pulizia automatica dei file temporanei
- Timeout per le richieste HTTP

## Gestione degli errori

L'API restituisce i seguenti codici di stato HTTP:

- `200 OK`: Immagine processata con successo
- `400 Bad Request`: URL non valido o parametri mancanti
- `401 Unauthorized`: API Key non valida
- `500 Internal Server Error`: Errore interno del server

## Performance e limitazioni

- Le immagini vengono scaricate e processate in memoria quando possibile
- I file temporanei vengono automaticamente eliminati dopo il processamento
- Timeout di 30 secondi per il download delle immagini
- Supporto per immagini di dimensioni ragionevoli (limitato dalla memoria disponibile)

## 🐳 Deployment con Docker

### Opzione 1: Build e run automatico
```bash
# Esegui lo script automatico
./docker-build.sh
```

### Opzione 2: Docker Compose (raccomandato)
```bash
# Copia e configura le variabili d'ambiente
cp .env.example .env
# Edita .env con le tue configurazioni

# Build e avvio con cache persistente
docker-compose up -d

# Per vedere i logs
docker-compose logs -f

# Per fermare
docker-compose down
```

### Opzione 3: Docker manuale
```bash
# Build dell'immagine con token HF (opzionale)
docker build \
  --build-arg HF_TOKEN=your-hf-token-here \
  -t removebg-api:latest .

# Run del container con volumi per cache
docker run -d \
  --name removebg-api \
  -p 8000:8000 \
  -e API_KEY=your-api-key-here \
  -e HF_TOKEN=your-hf-token-here \
  -e DEBUG=false \
  -v hf_cache:/app/.cache/huggingface \
  -v torch_cache:/app/.cache/torch \
  removebg-api:latest

# Verifica che sia in esecuzione
docker ps

# Logs
docker logs -f removebg-api
```

### Configurazione Docker con HuggingFace

**Setup completo con token HF:**
```bash
# File .env
API_KEY=your-secure-api-key
HF_TOKEN=hf_your_token_here
DEBUG=false

# Build con pre-download dei modelli
docker-compose build --build-arg HF_TOKEN=$HF_TOKEN

# Avvio con cache persistente
docker-compose up -d
```

**Vantaggi della configurazione avanzata:**
- ✅ **Pre-download modelli** durante il build (primo avvio più veloce)
- ✅ **Cache persistente** tra riavvii del container
- ✅ **Modelli RMBG-2.0** per qualità superiore
- ✅ **Memoria aumentata** per gestire modelli AI (4GB in produzione)

### Configurazione Docker

**Variabili d'ambiente per Docker:**
- `API_KEY`: Chiave API (default: demo-api-key-123)
- `HF_TOKEN`: Token HuggingFace per modelli migliori (opzionale)
- `DEBUG`: Modalità debug (default: false)
- `HOST`: Host interno (sempre 0.0.0.0 in Docker)
- `PORT`: Porta interna (sempre 8000 in Docker)

**Volumi Docker:**
- `hf_cache`: Cache modelli HuggingFace (persistente)
- `torch_cache`: Cache PyTorch (persistente)
- `./temp_images`: Directory immagini temporanee (opzionale)

**File di configurazione:**
- `Dockerfile`: Configurazione dell'immagine
- `docker-compose.yml`: Orchestrazione dei servizi
- `.dockerignore`: File da escludere dal build
- `docker-build.sh`: Script automatico di build e deploy

## Sviluppo

### Struttura del progetto

```
├── main.py              # Entry point dell'applicazione
├── image_processor.py   # Logica di processamento delle immagini
├── requirements.txt     # Dipendenze Python
├── Dockerfile          # Configurazione Docker
├── docker-compose.yml  # Orchestrazione Docker
├── docker-build.sh     # Script automatico Docker
├── .dockerignore       # File da escludere da Docker
├── .env                # Configurazione locale
├── .env.example        # Template di configurazione
├── .env.docker         # Template per Docker
└── README.md           # Questa documentazione
```

### Debug

Per abilitare la modalità debug, imposta `DEBUG=True` nel file `.env`. Questo abiliterà:
- Ricaricamento automatico del codice
- Documentazione Swagger su `/docs`
- Logging dettagliato

## Licenza

Questo progetto è distribuito sotto licenza MIT.