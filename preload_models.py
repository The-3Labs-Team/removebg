#!/usr/bin/env python3
"""
Script per pre-scaricare i modelli HuggingFace durante la build del Docker.
Questo script viene eseguito solo se è fornito un token HF.
"""

import os
import sys
import torch
from transformers import AutoModelForImageSegmentation

def preload_models():
    """Pre-scarica i modelli disponibili con il token HF fornito."""
    
    # Lista dei modelli da provare in ordine di preferenza
    models_to_try = [
        'briaai/RMBG-2.0',
        'briaai/RMBG-1.4',
        'Xenova/modnet'
    ]
    
    device = "cpu"  # Forza CPU durante il build
    models_loaded = 0
    
    print("🚀 Inizio pre-download dei modelli HuggingFace...")
    
    for model_name in models_to_try:
        try:
            print(f"📥 Tentativo download: {model_name}")
            
            # Prova a scaricare il modello
            model = AutoModelForImageSegmentation.from_pretrained(
                model_name,
                trust_remote_code=True,
                dtype=torch.float32,
                cache_dir='/app/.cache/huggingface/transformers'
            )
            
            print(f"✅ {model_name} scaricato con successo")
            models_loaded += 1
            
            # Per risparmiare spazio, non carichiamo tutti i modelli in memoria
            del model
            
        except Exception as e:
            print(f"⚠️  {model_name} non disponibile: {str(e)[:100]}...")
            continue
    
    if models_loaded > 0:
        print(f"🎉 Pre-download completato! {models_loaded} modelli scaricati.")
    else:
        print("⚠️  Nessun modello scaricato, verranno caricati al primo avvio.")
    
    return models_loaded > 0

if __name__ == "__main__":
    try:
        success = preload_models()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Errore durante il pre-download: {e}")
        sys.exit(1)