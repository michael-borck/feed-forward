#!/bin/bash
# Development environment with Docker

set -e

echo "🚀 Starting FeedForward in development mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your configuration"
fi

# Build and start development containers
echo "🔨 Building containers..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

echo "🏃 Starting services..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

echo "✅ Development environment stopped"