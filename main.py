import os
from typing import Optional
from functools import wraps
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from fastapi.responses import Response
from dotenv import load_dotenv
from image_processor import ImageProcessor
import logging

# Carica le variabili d'ambiente
load_dotenv()

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione
API_KEY = os.getenv("API_KEY", "default-api-key")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
TEMP_DIR = os.getenv("TEMP_DIR", "./temp_images")

# Inizializza FastAPI
app = FastAPI(
    title="Remove Background API",
    description="API per rimuovere lo sfondo dalle immagini usando rembg",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None
)

# Configurazione autenticazione API Key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: Optional[str] = Depends(api_key_header)):
    """Verifica l'API key."""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key non valida"
        )
    return api_key

# Inizializza il processore di immagini
image_processor = ImageProcessor(temp_dir=TEMP_DIR)


@app.get("/")
async def root():
    """Endpoint di stato dell'API."""
    return {
        "message": "Remove Background API",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/remove-background")
async def remove_background(
    image_url: str,
    api_key: str = Depends(get_api_key)
):
    """
    Rimuove lo sfondo da un'immagine.
    
    Args:
        image_url: URL dell'immagine da processare
        api_key: Chiave API per l'autenticazione (header X-API-Key)
    
    Returns:
        Immagine con sfondo rimosso in formato PNG
        
    Raises:
        HTTPException: Per errori di validazione, download o processamento
    """
    try:
        logger.info(f"Processando immagine da URL: {image_url}")
        
        # Verifica che l'URL sia fornito
        if not image_url or not image_url.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL dell'immagine è richiesto"
            )
        
        # Processa l'immagine
        processed_image_data = image_processor.process_image_from_url(image_url.strip())
        
        logger.info("Immagine processata con successo")
        
        # Restituisce l'immagine processata
        return Response(
            content=processed_image_data,
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=image_no_background.png"
            }
        )
        
    except ValueError as e:
        logger.warning(f"Errore di validazione: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Errore interno: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore interno del server durante il processamento dell'immagine"
        )


@app.post("/remove-background")
async def remove_background_post(
    image_url: str,
    api_key: str = Depends(get_api_key)
):
    """
    Alternativa POST per rimuovere lo sfondo da un'immagine.
    Utile per URL molto lunghi che potrebbero avere problemi con GET.
    """
    return await remove_background(image_url, api_key)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Avvio server su {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )