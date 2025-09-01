#!/bin/sh
set -e

# Start Ollama server in background
ollama serve &
pid=$!

# Wait for server to start
sleep 10

# Check and pull llama3.2 if missing
if ! ollama list | grep -q "llama3.2"; then
    echo "Pulling llama3.2"
    ollama pull llama3.2
else
    echo "llama3.2 already present"
fi

# Wait for server process
wait $pid