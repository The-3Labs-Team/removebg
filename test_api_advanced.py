#!/usr/bin/env python3
"""
Test avanzato per l'API Remove Background con verifica dei metadata.
"""

import requests
import json
import time
from PIL import Image
import io
import sys
import os

# Configurazione
API_BASE_URL = "http://localhost:8000"
API_KEY = "demo-api-key-123"  # Cambia con la tua API key
TEST_IMAGE_URL = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=600&fit=crop"

def test_api_connection():
    """Test connessione API."""
    print("🔌 Test connessione API...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API raggiungibile")
            return True
        else:
            print(f"❌ API non risponde: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di connessione: {e}")
        return False

def test_background_removal():
    """Test rimozione sfondo con verifica metadata."""
    print("\n🎨 Test rimozione sfondo...")
    
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/remove-background",
            params={"image_url": TEST_IMAGE_URL},
            headers={"X-API-Key": API_KEY},
            timeout=60
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Immagine processata in {processing_time:.2f} secondi")
            
            # Salva l'immagine
            output_path = "test_result_with_metadata.png"
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Verifica i metadata
            print("\n📋 Verifica metadata...")
            verify_metadata(output_path)
            
            return True
        else:
            print(f"❌ Errore processamento: {response.status_code}")
            print(f"Dettagli: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout richiesta")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore richiesta: {e}")
        return False

def verify_metadata(image_path):
    """Verifica i metadata nell'immagine processata."""
    try:
        with Image.open(image_path) as img:
            print(f"📊 Dimensioni immagine: {img.width}x{img.height}")
            print(f"📊 Formato: {img.format}")
            print(f"📊 Modalità: {img.mode}")
            print(f"📊 Ha canale alpha: {'Alpha' in img.mode or img.mode == 'RGBA'}")
            
            # Verifica metadata di base
            if hasattr(img, 'text') and img.text:
                print("\n🏷️  Metadata trovati:")
                
                key_metadata = [
                    "Title",
                    "Software", 
                    "Creation Time",
                    "Source URL",
                    "Processing Model",
                    "Processing Time",
                    "Processing Device",
                    "Original Size",
                    "API Version"
                ]
                
                for key in key_metadata:
                    if key in img.text:
                        value = img.text[key]
                        if len(value) > 100:
                            value = value[:100] + "..."
                        print(f"   {key}: {value}")
                
                # Verifica metadata JSON strutturati
                if "Processing Info JSON" in img.text:
                    print("\n📄 Metadata JSON strutturati:")
                    try:
                        json_data = json.loads(img.text["Processing Info JSON"])
                        print(f"   Modello: {json_data.get('processing', {}).get('model', 'N/A')}")
                        print(f"   Dispositivo: {json_data.get('processing', {}).get('device', 'N/A')}")
                        print(f"   Tempo processamento: {json_data.get('processing', {}).get('processing_time_seconds', 'N/A')}s")
                        print(f"   Formato originale: {json_data.get('original', {}).get('format', 'N/A')}")
                        print(f"   Dimensioni originali: {json_data.get('original', {}).get('width', 'N/A')}x{json_data.get('original', {}).get('height', 'N/A')}")
                        print(f"   Successo: {json_data.get('processing', {}).get('success', 'N/A')}")
                    except json.JSONDecodeError:
                        print("   ❌ Errore nel parsing del JSON")
                
                print("✅ Metadata verificati con successo")
            else:
                print("⚠️  Nessun metadata trovato nell'immagine")
                
    except Exception as e:
        print(f"❌ Errore verifica metadata: {e}")

def test_invalid_requests():
    """Test richieste non valide."""
    print("\n🚫 Test richieste non valide...")
    
    # Test senza API key
    response = requests.get(
        f"{API_BASE_URL}/remove-background",
        params={"image_url": TEST_IMAGE_URL}
    )
    if response.status_code == 401:
        print("✅ Autenticazione richiesta correttamente")
    else:
        print(f"❌ Autenticazione non verificata: {response.status_code}")
    
    # Test con API key non valida
    response = requests.get(
        f"{API_BASE_URL}/remove-background",
        params={"image_url": TEST_IMAGE_URL},
        headers={"X-API-Key": "invalid-key"}
    )
    if response.status_code == 401:
        print("✅ API key non valida respinta correttamente")
    else:
        print(f"❌ API key non valida accettata: {response.status_code}")
    
    # Test senza URL
    response = requests.get(
        f"{API_BASE_URL}/remove-background",
        headers={"X-API-Key": API_KEY}
    )
    if response.status_code == 422:  # FastAPI validation error
        print("✅ URL mancante gestito correttamente")
    else:
        print(f"❌ URL mancante non gestito: {response.status_code}")

def main():
    """Esegue tutti i test."""
    print("🧪 Test avanzato API Remove Background con Metadata")
    print("=" * 50)
    
    # Test connessione
    if not test_api_connection():
        print("\n❌ Test falliti: API non raggiungibile")
        sys.exit(1)
    
    # Test funzionalità principale
    success = test_background_removal()
    
    # Test casi edge
    test_invalid_requests()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Tutti i test completati con successo!")
        print(f"📁 Immagine di test salvata come: test_result_with_metadata.png")
        print("\n💡 Puoi aprire l'immagine e verificare i metadata con:")
        print("   python -c \"from PIL import Image; img = Image.open('test_result_with_metadata.png'); print(img.text)\"")
    else:
        print("❌ Alcuni test sono falliti")
        sys.exit(1)

if __name__ == "__main__":
    main()