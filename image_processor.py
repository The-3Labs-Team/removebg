import os
import tempfile
import uuid
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import requests
from PIL import Image, PngImagePlugin
import io
import logging
import warnings
import torch
from transformers import AutoModelForImageSegmentation
import torchvision.transforms as transforms
from datetime import datetime
import json

# Sopprimi i warning di deprecazione da timm
warnings.filterwarnings("ignore", category=FutureWarning, module="timm")

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Classe per gestire il download, processamento e rimozione delle immagini."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        # Crea la directory temporanea se non esiste
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Forza CPU-only per compatibilità
        self.device = "cpu"
        
        try:
            logger.info("Caricamento modello background removal (CPU-only)...")
            
            # Usa un modello alternativo open-access
            # Prova prima RMBG-2.0, poi fallback a modelli aperti
            models_to_try = [
                'briaai/RMBG-2.0',
                'briaai/RMBG-1.4', 
                'Xenova/modnet'
            ]
            
            model_loaded = False
            for model_name in models_to_try:
                try:
                    logger.info(f"Tentativo caricamento: {model_name}")
                    self.model = AutoModelForImageSegmentation.from_pretrained(
                        model_name,
                        trust_remote_code=True,
                        dtype=torch.float32
                    ).to(self.device)
                    self.model.eval()
                    logger.info(f"✅ Caricato con successo: {model_name}")
                    model_loaded = True
                    break
                except Exception as model_error:
                    logger.warning(f"❌ Fallito {model_name}: {model_error}")
                    continue
            
            if not model_loaded:
                raise Exception("Nessun modello disponibile")
            
            # Transform per preprocessing
            self.transform = transforms.Compose([
                transforms.Resize((1024, 1024)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            
            logger.info("RMBG-2.0 caricato con successo per foto prodotti (CPU)")
            
        except Exception as e:
            logger.error(f"Errore nel caricamento modelli Transformers: {e}")
            # Fallback a rembg con modelli ottimizzati per prodotti
            try:
                from rembg import new_session
                self.model = None
                
                # Prova i migliori modelli rembg per prodotti
                models_to_try = ['birefnet-general', 'isnet-general-use', 'silueta']
                
                for model_name in models_to_try:
                    try:
                        logger.info(f"Tentativo rembg: {model_name}")
                        self.session = new_session(model_name)
                        logger.info(f"✅ rembg caricato: {model_name}")
                        break
                    except Exception as model_error:
                        logger.warning(f"❌ Fallito rembg {model_name}: {model_error}")
                        continue
                else:
                    # Se nessun modello specifico funziona, usa il default
                    logger.info("Uso modello rembg default")
                    self.session = new_session()
                    
            except Exception as fallback_error:
                logger.error(f"Errore anche nel fallback rembg: {fallback_error}")
                raise Exception("Impossibile inizializzare nessun modello di background removal")
    
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
    
    def remove_background_rmbg2(self, input_path: str) -> tuple[str, Dict[str, Any]]:
        """
        Rimuove lo sfondo usando RMBG-2.0 di BriaAI (CPU-only).
        
        Args:
            input_path: Percorso dell'immagine di input
            
        Returns:
            tuple: (Percorso dell'immagine processata, informazioni di processamento)
        """
        import time
        start_time = time.time()
        
        try:
            # Carica e preprocessa l'immagine
            image = Image.open(input_path).convert('RGB')
            original_size = image.size
            original_format = image.format or 'unknown'
            
            # Applica le trasformazioni
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Inferenza (CPU-only)
            with torch.no_grad():
                outputs = self.model(input_tensor)
                
                # Debug: vediamo cosa restituisce il modello
                logger.info(f"Tipo output modello: {type(outputs)}")
                if isinstance(outputs, (list, tuple)):
                    logger.info(f"Lunghezza lista output: {len(outputs)}")
                    logger.info(f"Tipo ultimo elemento: {type(outputs[-1])}")
                
                # Gestisci diversi formati di output
                if isinstance(outputs, (list, tuple)):
                    # Se è una lista, prendi l'ultimo elemento
                    preds = outputs[-1]
                else:
                    # Se è un tensor diretto
                    preds = outputs
                
                # Applica sigmoid se necessario
                if hasattr(preds, 'sigmoid'):
                    preds = preds.sigmoid()
                else:
                    # Clamp tra 0 e 1 se sigmoid non è disponibile
                    preds = torch.clamp(preds, 0, 1)
                
                preds = preds.cpu()
            
            # Post-processing
            pred = preds[0].squeeze()
            
            # Converti in PIL Image
            if pred.dim() == 3:
                pred = pred[0]  # Prendi il primo canale se ci sono più canali
            
            pred_pil = transforms.ToPILImage()(pred)
            mask = pred_pil.resize(original_size)
            
            # Applica la maschera all'immagine originale
            image.putalpha(mask)
            
            # Genera il percorso di output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.temp_dir, f"{base_name}_nobg.png")
            
            # Salva l'immagine
            image.save(output_path, 'PNG')
            
            processing_time = time.time() - start_time
            
            # Raccogli informazioni di processamento
            processing_info = {
                'model_used': 'RMBG-2.0 (Transformers)',
                'device': self.device,
                'processing_time': processing_time,
                'original_format': original_format,
                'original_width': original_size[0],
                'original_height': original_size[1],
                'original_size': os.path.getsize(input_path) if os.path.exists(input_path) else 0
            }
            
            logger.info(f"Sfondo rimosso con RMBG-2.0: {output_path} (tempo: {processing_time:.2f}s)")
            return output_path, processing_info
            
        except Exception as e:
            raise IOError(f"Errore con RMBG-2.0: {str(e)}")
    
    def remove_background_fallback(self, input_path: str) -> tuple[str, Dict[str, Any]]:
        """Fallback usando rembg se RMBG-2.0 non è disponibile."""
        import time
        start_time = time.time()
        
        try:
            from rembg import remove
            
            # Ottieni informazioni sull'immagine originale
            with Image.open(input_path) as original_img:
                original_size = original_img.size
                original_format = original_img.format or 'unknown'
            
            with open(input_path, 'rb') as f:
                input_data = f.read()
            
            output_data = remove(input_data, session=self.session)
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.temp_dir, f"{base_name}_nobg.png")
            
            with open(output_path, 'wb') as f:
                f.write(output_data)
            
            processing_time = time.time() - start_time
            
            # Raccogli informazioni di processamento
            processing_info = {
                'model_used': 'rembg (fallback)',
                'device': 'cpu',
                'processing_time': processing_time,
                'original_format': original_format,
                'original_width': original_size[0],
                'original_height': original_size[1],
                'original_size': os.path.getsize(input_path) if os.path.exists(input_path) else 0
            }
            
            logger.info(f"Sfondo rimosso con rembg fallback: {output_path} (tempo: {processing_time:.2f}s)")
            return output_path, processing_info
            
        except Exception as e:
            raise IOError(f"Errore con fallback rembg: {str(e)}")
    
    def remove_background(self, input_path: str) -> tuple[str, Dict[str, Any]]:
        """
        Rimuove lo sfondo dall'immagine usando RMBG-2.0 o fallback.
        
        Args:
            input_path: Percorso dell'immagine di input
            
        Returns:
            tuple: (Percorso dell'immagine processata, informazioni di processamento)
            
        Raises:
            IOError: Se non è possibile processare l'immagine
        """
        if hasattr(self, 'model') and self.model is not None:
            # Usa RMBG-2.0
            return self.remove_background_rmbg2(input_path)
        else:
            # Fallback a rembg
            return self.remove_background_fallback(input_path)
    
    def add_metadata_to_image(self, image_path: str, original_url: str, processing_info: Dict[str, Any]) -> None:
        """
        Aggiunge metadata dettagliati all'immagine PNG processata.
        
        Args:
            image_path: Percorso dell'immagine PNG
            original_url: URL originale dell'immagine
            processing_info: Informazioni sul processamento
        """
        try:
            # Apri l'immagine esistente
            with Image.open(image_path) as img:
                # Crea i metadata personalizzati
                metadata = PngImagePlugin.PngInfo()
                
                # Informazioni base
                metadata.add_text("Title", "Background Removed Image")
                metadata.add_text("Description", "Image processed with AI background removal")
                metadata.add_text("Software", "RemoveBG API v1.0.0")
                metadata.add_text("Creation Time", datetime.now().isoformat())
                
                # Informazioni sulla sorgente
                metadata.add_text("Source URL", original_url)
                metadata.add_text("Original Format", processing_info.get('original_format', 'unknown'))
                metadata.add_text("Original Size", f"{processing_info.get('original_width', 0)}x{processing_info.get('original_height', 0)}")
                
                # Informazioni sul processamento
                metadata.add_text("Processing Model", processing_info.get('model_used', 'unknown'))
                metadata.add_text("Processing Device", processing_info.get('device', 'cpu'))
                metadata.add_text("Processing Time", f"{processing_info.get('processing_time', 0):.2f}s")
                
                # Informazioni tecniche
                metadata.add_text("Output Format", "PNG")
                metadata.add_text("Alpha Channel", "Yes")
                metadata.add_text("Color Space", "RGB+Alpha")
                
                # Informazioni sul processore
                metadata.add_text("Processor", "AI Background Removal Service")
                metadata.add_text("API Version", "1.0.0")
                
                # Metadata strutturati in JSON
                processing_metadata = {
                    "processing": {
                        "timestamp": datetime.now().isoformat(),
                        "model": processing_info.get('model_used', 'unknown'),
                        "device": processing_info.get('device', 'cpu'),
                        "processing_time_seconds": processing_info.get('processing_time', 0),
                        "success": True
                    },
                    "original": {
                        "url": original_url,
                        "format": processing_info.get('original_format', 'unknown'),
                        "width": processing_info.get('original_width', 0),
                        "height": processing_info.get('original_height', 0),
                        "file_size_bytes": processing_info.get('original_size', 0)
                    },
                    "output": {
                        "format": "PNG",
                        "has_alpha": True,
                        "width": img.width,
                        "height": img.height
                    }
                }
                
                metadata.add_text("Processing Info JSON", json.dumps(processing_metadata, indent=2))
                
                # Salva l'immagine con i metadata
                img.save(image_path, "PNG", pnginfo=metadata, optimize=True)
                
                logger.info(f"Metadata aggiunti all'immagine: {image_path}")
                
        except Exception as e:
            logger.warning(f"Errore nell'aggiunta dei metadata: {e}")
            # Non interrompe l'esecuzione se i metadata falliscono

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
            bytes: Dati dell'immagine processata con metadata
            
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
            
            # Rimozione dello sfondo con informazioni di processamento
            output_path, processing_info = self.remove_background(input_path)
            
            # Aggiungi metadata dettagliati all'immagine
            self.add_metadata_to_image(output_path, url, processing_info)
            
            # Leggi i dati dell'immagine processata con metadata
            with open(output_path, 'rb') as f:
                result_data = f.read()
            
            return result_data
            
        finally:
            # Pulizia dei file temporanei
            if input_path:
                self.cleanup_file(input_path)
            if output_path:
                self.cleanup_file(output_path)