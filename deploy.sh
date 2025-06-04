#!/bin/bash

# Deep Research AI - Deployment Script for Azure
# This script builds and deploys the application using Docker

set -e  # Exit on any error

echo "🚀 Starting Deep Research AI deployment..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your settings."
    echo "   cp .env.example .env"
    echo "   # Then edit .env with your Azure OpenAI and other settings"
    exit 1
fi

echo "✅ Environment file found"

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required environment variables
required_vars=("AZURE_OPENAI_API_KEY" "AZURE_OPENAI_ENDPOINT" "POSTGRES_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set in .env file"
        exit 1
    fi
done

echo "✅ Required environment variables validated"

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "🏃 Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker-compose -f docker-compose.production.yml ps | grep -q "healthy"; then
        echo "✅ Services are healthy!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Services failed to start properly after $max_attempts attempts"
        echo "📋 Service status:"
        docker-compose -f docker-compose.production.yml ps
        echo "📋 Logs:"
        docker-compose -f docker-compose.production.yml logs
        exit 1
    fi
    
    echo "⏳ Attempt $attempt/$max_attempts - waiting for services..."
    sleep 10
    ((attempt++))
done

# Display service information
echo "🎉 Deployment successful!"
echo ""
echo "📋 Service Information:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Deep Research AI:  http://localhost:8000"
echo "🔍 API Endpoint:      http://localhost:8000/docs"
echo "📊 Health Check:      http://localhost:8000/health"
echo "🗄️  PostgreSQL:       localhost:5432"
echo "🔴 Redis:             localhost:6379"
echo ""
echo "🔧 Management Commands:"
echo "  View logs:          docker-compose -f docker-compose.production.yml logs -f"
echo "  Stop services:      docker-compose -f docker-compose.production.yml down"
echo "  Restart services:   docker-compose -f docker-compose.production.yml restart"
echo "  View status:        docker-compose -f docker-compose.production.yml ps"
echo ""
echo "🚀 Your Deep Research AI is now running!"
