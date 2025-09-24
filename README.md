# Remove Background API

API HTTP per rimuovere lo sfondo dalle immagini utilizzando la libreria `rembg` con modello **birefnet-general** ottimizzato per foto di prodotti.

## Caratteristiche

- ✅ API HTTP protetta da chiave API
- ✅ Download automatico delle immagini da URL
- ✅ Rimozione dello sfondo usando rembg con modello birefnet-general
- ✅ Ottimizzato per foto di prodotti e oggetti
- ✅ Pulizia automatica dei file temporanei
- ✅ Gestione degli errori completa
- ✅ Logging strutturato
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
   ```
   API_KEY=your-secret-api-key-here
   HOST=0.0.0.0
   PORT=8000
   DEBUG=False
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
- `DEBUG`: Modalità debug (default: False)
- `TEMP_DIR`: Directory per i file temporanei (opzionale)

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
# Build e avvio
docker-compose up -d

# Per vedere i logs
docker-compose logs -f

# Per fermare
docker-compose down
```

### Opzione 3: Docker manuale
```bash
# Build dell'immagine
docker build -t removebg-api:latest .

# Run del container
docker run -d \
  --name removebg-api \
  -p 8000:8000 \
  -e API_KEY=your-api-key-here \
  -e DEBUG=false \
  removebg-api:latest

# Verifica che sia in esecuzione
docker ps

# Logs
docker logs -f removebg-api
```

### Configurazione Docker

**Variabili d'ambiente per Docker:**
- `API_KEY`: Chiave API (default: demo-api-key-123)
- `DEBUG`: Modalità debug (default: false)
- `HOST`: Host interno (sempre 0.0.0.0 in Docker)
- `PORT`: Porta interna (sempre 8000 in Docker)

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