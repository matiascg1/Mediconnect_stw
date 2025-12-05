#!/bin/bash

echo "🚀 Setting up Mediconnect Project..."

# Check if .env exists, if not create it
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    
    # Generate random JWT secret
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -hex 32)
        sed -i '' "s/your-secret-key-change-in-production/$JWT_SECRET/" .env
        echo "✅ Generated secure JWT secret"
    fi
    
    echo ""
    echo "⚠️  Please edit .env file with your configuration"
    echo "   - Open .env in a text editor"
    echo "   - Verify database credentials"
    echo "   - Save the file"
    echo ""
    read -p "Press Enter after you've reviewed the .env file..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Build images
echo "🔨 Building Docker images..."
docker-compose build

echo "🐳 Starting Docker containers..."
docker-compose up -d

echo "⏳ Waiting for services to start (this may take a minute)..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."

if docker ps | grep -q mediconnect_mysql; then
    echo "✅ MySQL is running"
else
    echo "❌ MySQL failed to start. Check logs with: docker logs mediconnect_mysql"
fi

if docker ps | grep -q mediconnect_redis; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
fi

if docker ps | grep -q mediconnect_api_gateway; then
    echo "✅ API Gateway is running"
else
    echo "❌ API Gateway failed to start"
fi

echo ""
echo "✅ Setup completed!"
echo ""
echo "📋 Services running:"
echo "   - API Gateway: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - MySQL: localhost:3307 (user: mediconnect_user)"
echo "   - Redis: localhost:6379"
echo ""
echo "🔑 Default credentials:"
echo "   - Admin: admin@mediconnect.com / admin123"
echo "   - Doctor: doctor1@mediconnect.com / admin123"
echo "   - Patient: patient1@mediconnect.com / admin123"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose logs"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo "   - Rebuild: docker-compose up --build -d"
