#!/bin/bash

# Script di avvio per l'API Remove Background

echo "🚀 Avvio API Remove Background..."

# Verifica che il virtual environment sia attivo
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment attivo: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment non rilevato"
    echo "💡 Considera di attivare il virtual environment con:"
    echo "   source .venv/bin/activate"
fi

# Verifica che il file .env esista
if [ ! -f .env ]; then
    echo "⚠️  File .env non trovato, copia da .env.example"
    cp .env.example .env
    echo "📝 File .env creato, modifica la configurazione se necessario"
fi

# Verifica le dipendenze
echo "🔍 Verifica dipendenze..."
python -c "import fastapi, uvicorn, rembg" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Dipendenze OK"
else
    echo "❌ Dipendenze mancanti, installa con:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Avvia il server
echo "🌟 Avvio del server..."
echo "📍 API disponibile su: http://localhost:8000"
echo "📚 Documentazione su: http://localhost:8000/docs"
echo "💻 Premi Ctrl+C per fermare il server"
echo ""

python main.py