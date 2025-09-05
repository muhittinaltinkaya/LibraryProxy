#!/bin/bash

# LibProxy Startup Script
echo "Starting LibProxy - Dynamic Proxy System for Electronic Journal Access"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "Please edit .env file with your configuration before running again."
    exit 1
fi

# Start services
echo "Starting services with docker-compose..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "Checking service status..."
docker-compose ps

# Run database migrations
echo "Running database migrations..."
docker-compose exec backend flask db upgrade

echo "LibProxy is starting up!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:5000"
echo "HAProxy Stats: http://localhost:8404/stats"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "To stop the services, run: docker-compose down"
