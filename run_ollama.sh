#!/bin/bash

echo "Starting Ollama server..."

# Start Ollama in the background
ollama serve &

# Wait until Ollama is ready
until curl -s http://localhost:11434 > /dev/null; do
    echo "Waiting for Ollama to be ready..."
    sleep 2
done

# Pull the model
echo "Pulling Gemma..."
ollama pull gemma:2b

# Optional: keep container alive for logs
tail -f /dev/null
