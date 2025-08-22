#!/bin/bash
# Production deployment with Docker

set -e

echo "🚀 Deploying FeedForward in production mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: No .env file found!"
    echo "Please create .env with production configuration"
    exit 1
fi

# Pull latest images
echo "📦 Pulling latest images..."
docker-compose pull

# Build application
echo "🔨 Building application..."
docker-compose build

# Start production services
echo "🏃 Starting production services..."
docker-compose --profile production up -d

# Wait for health check
echo "⏳ Waiting for application to be healthy..."
sleep 10

# Check health
if curl -f http://localhost:5001/ > /dev/null 2>&1; then
    echo "✅ FeedForward is running successfully!"
    echo "🌐 Application available at http://localhost:5001"
    
    # Show logs
    echo ""
    echo "📋 Recent logs:"
    docker-compose logs --tail=20 feedforward
else
    echo "❌ Health check failed!"
    echo "Check logs with: docker-compose logs feedforward"
    exit 1
fi