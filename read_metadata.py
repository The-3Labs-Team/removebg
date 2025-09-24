#!/usr/bin/env python3
"""
Script per leggere e visualizzare i metadata di un'immagine processata.
"""

import sys
import json
from PIL import Image

def read_metadata(image_path):
    """Legge e visualizza i metadata di un'immagine PNG."""
    try:
        with Image.open(image_path) as img:
            print(f"📄 File: {image_path}")
            print(f"📊 Formato: {img.format}")
            print(f"📊 Dimensioni: {img.width}x{img.height}")
            print(f"📊 Modalità: {img.mode}")
            print(f"📊 Ha trasparenza: {'A' in img.mode}")
            
            if hasattr(img, 'text') and img.text:
                print("\n🏷️  METADATA STANDARD:")
                print("-" * 40)
                
                # Metadata ordinati per categoria
                categories = {
                    "Informazioni Base": ["Title", "Description", "Software", "Creation Time", "API Version"],
                    "Sorgente": ["Source URL", "Original Format", "Original Size"],
                    "Processamento": ["Processing Model", "Processing Device", "Processing Time"],
                    "Output": ["Output Format", "Alpha Channel", "Color Space"]
                }
                
                for category, keys in categories.items():
                    found_any = False
                    for key in keys:
                        if key in img.text:
                            if not found_any:
                                print(f"\n📂 {category}:")
                                found_any = True
                            print(f"   {key}: {img.text[key]}")
                
                # Metadata JSON strutturati
                if "Processing Info JSON" in img.text:
                    print("\n🔧 METADATA JSON STRUTTURATI:")
                    print("-" * 40)
                    try:
                        json_data = json.loads(img.text["Processing Info JSON"])
                        print(json.dumps(json_data, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError as e:
                        print(f"❌ Errore parsing JSON: {e}")
                
                # Altri metadata
                other_metadata = {k: v for k, v in img.text.items() 
                                if k not in [item for sublist in categories.values() for item in sublist] 
                                and k != "Processing Info JSON"}
                
                if other_metadata:
                    print("\n📋 ALTRI METADATA:")
                    print("-" * 40)
                    for key, value in other_metadata.items():
                        if len(value) > 100:
                            value = value[:100] + "..."
                        print(f"   {key}: {value}")
                
            else:
                print("\n⚠️  Nessun metadata trovato nell'immagine")
                
    except FileNotFoundError:
        print(f"❌ File non trovato: {image_path}")
    except Exception as e:
        print(f"❌ Errore nella lettura dell'immagine: {e}")

def main():
    """Script principale."""
    if len(sys.argv) != 2:
        print("Uso: python read_metadata.py <percorso_immagine>")
        print("\nEsempio:")
        print("  python read_metadata.py test_result_with_metadata.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    print("🔍 LETTORE METADATA IMMAGINI PROCESSATE")
    print("=" * 50)
    
    read_metadata(image_path)

if __name__ == "__main__":
    main()