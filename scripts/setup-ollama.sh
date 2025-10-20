#!/bin/bash

# Setup script for Ollama LLM service
# This script pulls the configured Ollama model and verifies the service is working

set -e

# Model configuration (can be overridden via environment variable)
MODEL_NAME="${OLLAMA_MODEL:-llama3.2:1b}"

echo "=================================================="
echo "Setting up Ollama LLM Service"
echo "=================================================="
echo "Model: $MODEL_NAME"
echo ""

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

# Pull the configured model
echo ""
echo "Pulling model: $MODEL_NAME"
echo "This may take several minutes depending on your internet connection"
echo ""

docker compose -f docker/docker-compose.dev.yml exec ollama ollama pull $MODEL_NAME

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
if docker compose -f docker/docker-compose.dev.yml exec ollama ollama list | grep -q "$MODEL_NAME"; then
    echo "✓ Model is available"
else
    echo "Warning: Model not found in list, but pull succeeded"
fi

# Test model with a simple prompt
echo ""
echo "Testing model with a simple prompt..."
TEST_RESPONSE=$(docker compose -f docker/docker-compose.dev.yml exec ollama ollama run $MODEL_NAME "Say 'Hello from Llama!'")

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
echo "Model: $MODEL_NAME"
echo "Endpoint: http://localhost:11434"
echo ""
echo "You can now use LLM-based feature extraction in the ML pipeline."
echo ""
echo "To use a different model, set OLLAMA_MODEL environment variable:"
echo "  OLLAMA_MODEL=llama3.2:3b ./scripts/setup-ollama.sh"
echo ""
