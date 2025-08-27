#!/bin/bash
# Quick setup script for VPS deployment

echo "Setting up FeedForward environment..."

# Copy example env if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
    echo "Please edit .env and add your configuration:"
    echo "  - SMTP settings for email"
    echo "  - At least one LLM API key"
    echo "  - Update APP_DOMAIN to your domain"
else
    echo ".env already exists"
fi

# Fix docker-compose vs docker compose
if ! command -v docker-compose &> /dev/null; then
    echo "Creating docker-compose alias..."
    echo 'alias docker-compose="docker compose"' >> ~/.bashrc
    echo 'alias docker-compose="docker compose"' >> ~/.zshrc 2>/dev/null || true
    echo "Alias created. Run 'source ~/.bashrc' or restart shell"
fi

echo "Ready to build: docker compose build"
echo "Then run: docker compose up -d"
