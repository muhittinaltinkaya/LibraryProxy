#!/bin/bash

# LibProxy Production Deployment Script
# For server: 80.251.40.216

echo "🚀 Starting LibProxy production deployment..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Set production environment
export COMPOSE_FILE=docker-compose.prod.yml

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Remove old images (optional, comment out if you want to keep them)
echo "🧹 Cleaning up old images..."
docker system prune -f

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend flask db upgrade

# Create/update admin user
echo "👤 Creating/updating admin user..."
docker-compose -f docker-compose.prod.yml exec -T backend python /app/create_admin_user.py

# Show logs
echo "📋 Showing recent logs..."
docker-compose -f docker-compose.prod.yml logs --tail=50

echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://80.251.40.216:3000"
echo "   Backend API: http://80.251.40.216:5001/api"
echo "   HAProxy Stats: http://80.251.40.216:8404/stats"
echo "   Proxy Access: http://80.251.40.216"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart services: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "⚠️  Important Security Notes:"
echo "   1. Change JWT_SECRET_KEY in env.production"
echo "   2. Change POSTGRES_PASSWORD in env.production"
echo "   3. Set up SSL/HTTPS for production"
echo "   4. Configure firewall rules"
echo "   5. Set up backup strategy"
echo ""
