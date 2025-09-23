#!/usr/bin/env python3
"""
Test script per l'API Remove Background
"""
import requests
import sys
import os

def test_api():
    """Test dell'API Remove Background"""
    
    # Configurazione
    base_url = "http://localhost:8000"
    api_key = "demo-api-key-123"  # Dalla configurazione .env
    
    # URL di esempio di un'immagine
    test_image_url = "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=500"
    
    print("🧪 Test API Remove Background")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Test health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check OK")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Errore nella connessione: {e}")
        return False
    
    # Test 2: Endpoint senza API key
    print("2. Test senza API key...")
    try:
        response = requests.get(f"{base_url}/remove-background?image_url={test_image_url}")
        if response.status_code == 401:
            print("   ✅ Autenticazione correttamente richiesta")
        else:
            print(f"   ❌ Comportamento inaspettato: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Test 3: Endpoint con API key sbagliata
    print("3. Test con API key sbagliata...")
    try:
        response = requests.get(
            f"{base_url}/remove-background?image_url={test_image_url}",
            headers={"X-API-Key": "wrong-key"}
        )
        if response.status_code == 401:
            print("   ✅ API key sbagliata correttamente rifiutata")
        else:
            print(f"   ❌ Comportamento inaspettato: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Test 4: URL non valido
    print("4. Test con URL non valido...")
    try:
        response = requests.get(
            f"{base_url}/remove-background?image_url=not-a-valid-url",
            headers={"X-API-Key": api_key}
        )
        if response.status_code == 400:
            print("   ✅ URL non valido correttamente rifiutato")
        else:
            print(f"   ❌ Comportamento inaspettato: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Test 5: Processamento immagine reale
    print("5. Test processamento immagine...")
    try:
        response = requests.get(
            f"{base_url}/remove-background?image_url={test_image_url}",
            headers={"X-API-Key": api_key}
        )
        
        if response.status_code == 200:
            # Salva l'immagine risultante
            output_file = "test_result.png"
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"   ✅ Immagine processata con successo!")
            print(f"   📁 Salvata come: {output_file}")
            print(f"   📊 Dimensione: {file_size:,} bytes")
            
            # Verifica che sia un PNG valido
            if response.content.startswith(b'\x89PNG'):
                print("   ✅ File PNG valido")
            else:
                print("   ⚠️  File non sembra essere un PNG valido")
                
        else:
            print(f"   ❌ Processamento fallito: {response.status_code}")
            print(f"   📝 Dettagli: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Test completati!")
    print("\n💡 Suggerimenti:")
    print("   - Verifica che il server sia in esecuzione su localhost:8000")
    print("   - Controlla i log del server per eventuali errori")
    print("   - Assicurati di avere una connessione internet per scaricare l'immagine di test")

if __name__ == "__main__":
    test_api()