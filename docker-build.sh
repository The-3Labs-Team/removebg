docker compose build --no-cachedocker compose build --no-cachedocker compose down
docker compose build --no-cache
docker compose up -d#!/bin/bash

# Script per costruire e avviare il container Docker
set -e

echo "🐳 Docker Build & Deploy Script"
echo "================================"

# Verifica che Docker sia in esecuzione
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker non è in esecuzione. Avvia Docker Desktop."
    exit 1
fi

# Build dell'immagine
echo "🔨 Building Docker image..."
docker build -t removebg-api:latest .

echo "✅ Immagine creata con successo!"

# Opzioni per l'avvio
echo ""
echo "🚀 Opzioni di avvio:"
echo "1. docker compose up (raccomandato)"
echo "2. docker run manuale"
echo ""

read -p "Scegli un'opzione (1 o 2): " choice

case $choice in
    1)
        echo "🚀 Avvio con docker compose..."
        if [ ! -f .env ]; then
            echo "⚠️  File .env non trovato, copio da .env.docker"
            cp .env.docker .env
        fi
        docker compose up -d
        echo "✅ Servizio avviato!"
        echo "📍 API disponibile su: http://localhost:8000"
        echo "📚 Documentazione su: http://localhost:8000/docs"
        echo ""
        echo "Per vedere i logs: docker compose logs -f"
        echo "Per fermare: docker compose down"
        ;;
    2)
        echo "🚀 Avvio manuale..."
        docker run -d \
            --name removebg-api \
            -p 8000:8000 \
            -e API_KEY=demo-api-key-123 \
            -e DEBUG=false \
            removebg-api:latest
        echo "✅ Container avviato!"
        echo "📍 API disponibile su: http://localhost:8000"
        echo ""
        echo "Per vedere i logs: docker logs -f removebg-api"
        echo "Per fermare: docker stop removebg-api && docker rm removebg-api"
        ;;
    *)
        echo "❌ Opzione non valida"
        exit 1
        ;;
esac