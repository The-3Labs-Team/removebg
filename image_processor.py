import os
import tempfile
import uuid
from typing import Optional
from urllib.parse import urlparse
import requests
from PIL import Image
from rembg import remove, new_session
import io
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Classe per gestire il download, processamento e rimozione delle immagini."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        # Crea la directory temporanea se non esiste
        os.makedirs(self.temp_dir, exist_ok=True)
        # Inizializza il modello birefnet-general per foto di prodotti
        self.session = new_session('birefnet-general')
        logger.info("Inizializzato modello birefnet-general per foto prodotti")
    
    def is_valid_image_url(self, url: str) -> bool:
        """Verifica se l'URL è valido e punta a un'immagine."""
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False
            
            # Verifica l'estensione del file
            valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
            path_lower = parsed.path.lower()
            
            return any(path_lower.endswith(ext) for ext in valid_extensions)
        except Exception:
            return False
    
    def download_image(self, url: str) -> str:
        """
        Scarica un'immagine dall'URL e la salva temporaneamente.
        
        Args:
            url: URL dell'immagine da scaricare
            
        Returns:
            str: Percorso del file temporaneo
            
        Raises:
            ValueError: Se l'URL non è valido
            requests.RequestException: Se il download fallisce
            IOError: Se non è possibile salvare il file
        """
        if not self.is_valid_image_url(url):
            raise ValueError("URL dell'immagine non valido")
        
        # Genera un nome file univoco
        file_id = str(uuid.uuid4())
        
        try:
            # Scarica l'immagine
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Verifica il content-type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                raise ValueError("L'URL non punta a un'immagine valida")
            
            # Determina l'estensione del file dal content-type
            extension_map = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/bmp': '.bmp',
                'image/tiff': '.tiff',
                'image/webp': '.webp'
            }
            
            extension = extension_map.get(content_type, '.jpg')
            temp_path = os.path.join(self.temp_dir, f"{file_id}_original{extension}")
            
            # Salva il file
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verifica che il file sia effettivamente un'immagine valida
            try:
                with Image.open(temp_path) as img:
                    img.verify()
            except Exception:
                os.remove(temp_path)
                raise ValueError("File scaricato non è un'immagine valida")
            
            return temp_path
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Errore nel download dell'immagine: {str(e)}")
        except Exception as e:
            raise IOError(f"Errore nel salvataggio dell'immagine: {str(e)}")
    
    def remove_background(self, input_path: str) -> str:
        """
        Rimuove lo sfondo dall'immagine e salva il risultato.
        
        Args:
            input_path: Percorso dell'immagine di input
            
        Returns:
            str: Percorso dell'immagine processata
            
        Raises:
            IOError: Se non è possibile processare l'immagine
        """
        try:
            # Leggi l'immagine
            with open(input_path, 'rb') as f:
                input_data = f.read()
            
            # Rimuovi lo sfondo usando il modello birefnet-general
            output_data = remove(input_data, session=self.session)
            
            # Genera il percorso di output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.temp_dir, f"{base_name}_nobg.png")
            
            # Salva l'immagine processata
            with open(output_path, 'wb') as f:
                f.write(output_data)
            
            return output_path
            
        except Exception as e:
            raise IOError(f"Errore nella rimozione dello sfondo: {str(e)}")
    
    def cleanup_file(self, file_path: str) -> None:
        """
        Elimina un file dal disco.
        
        Args:
            file_path: Percorso del file da eliminare
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            # Log dell'errore ma non interrompe l'esecuzione
            pass
    
    def process_image_from_url(self, url: str) -> bytes:
        """
        Processo completo: scarica, processa e pulisce.
        
        Args:
            url: URL dell'immagine da processare
            
        Returns:
            bytes: Dati dell'immagine processata
            
        Raises:
            ValueError: Se l'URL non è valido
            requests.RequestException: Se il download fallisce
            IOError: Se il processamento fallisce
        """
        input_path = None
        output_path = None
        
        try:
            # Download dell'immagine
            input_path = self.download_image(url)
            
            # Rimozione dello sfondo
            output_path = self.remove_background(input_path)
            
            # Leggi i dati dell'immagine processata
            with open(output_path, 'rb') as f:
                result_data = f.read()
            
            return result_data
            
        finally:
            # Pulizia dei file temporanei
            if input_path:
                self.cleanup_file(input_path)
            if output_path:
                self.cleanup_file(output_path)