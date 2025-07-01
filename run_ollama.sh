#!/bin/bash

echo "Starting Ollama server..."
ollama serve &

sleep 5

echo "Pulling Gemma"
ollama pull gemma:2b

ollama run gemma:2b