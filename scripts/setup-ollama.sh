#!/bin/bash

# Setup script for Ollama LLM service
# This script pulls the Llama 3.2 1B model and verifies the Ollama service is working

set -e

echo "=================================================="
echo "Setting up Ollama LLM Service"
echo "=================================================="

# Check if Ollama container is running
if ! docker compose -f docker/docker-compose.dev.yml ps ollama | grep -q "running"; then
    echo "Error: Ollama service is not running"
    echo "Please start services with: ./scripts/start-server.sh"
    exit 1
fi

echo "✓ Ollama service is running"

# Wait for Ollama to be healthy
echo "Waiting for Ollama to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker compose -f docker/docker-compose.dev.yml exec ollama curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is ready"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Error: Ollama service did not become healthy in time"
    exit 1
fi

# Pull Llama 3.2 1B model
echo ""
echo "Pulling Llama 3.2 1B model..."
echo "This may take several minutes depending on your internet connection"
echo ""

docker compose -f docker/docker-compose.dev.yml exec ollama ollama pull llama3.2:1b

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Model pulled successfully"
else
    echo ""
    echo "Error: Failed to pull model"
    exit 1
fi

# Verify model is available
echo ""
echo "Verifying model availability..."
if docker compose -f docker/docker-compose.dev.yml exec ollama ollama list | grep -q "llama3.2:1b"; then
    echo "✓ Model is available"
else
    echo "Warning: Model not found in list, but pull succeeded"
fi

# Test model with a simple prompt
echo ""
echo "Testing model with a simple prompt..."
TEST_RESPONSE=$(docker compose -f docker/docker-compose.dev.yml exec ollama ollama run llama3.2:1b "Say 'Hello from Llama!'")

if [ $? -eq 0 ]; then
    echo "✓ Model test successful"
    echo "Response: $TEST_RESPONSE"
else
    echo "Error: Model test failed"
    exit 1
fi

echo ""
echo "=================================================="
echo "Ollama setup complete!"
echo "=================================================="
echo ""
echo "Model: llama3.2:1b"
echo "Endpoint: http://localhost:11434"
echo ""
echo "You can now use LLM-based feature extraction in the ML pipeline."
echo ""
