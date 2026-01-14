#!/bin/bash

set -e

echo "🚀 CyberShield Test Setup Script"
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

# Build and start services
echo -e "${YELLOW}🔨 Building and starting services...${NC}"
docker-compose -f docker-compose.test.yml up -d --build

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}🏥 Checking service health...${NC}"

# Wait for PostgreSQL
until docker-compose -f docker-compose.test.yml exec -T postgres pg_isready -U cybershield > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo -e "${GREEN}✅ PostgreSQL is ready${NC}"

# Wait for Redis
until docker-compose -f docker-compose.test.yml exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo "Waiting for Redis..."
    sleep 2
done
echo -e "${GREEN}✅ Redis is ready${NC}"

# Wait for MongoDB
until docker-compose -f docker-compose.test.yml exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    echo "Waiting for MongoDB..."
    sleep 2
done
echo -e "${GREEN}✅ MongoDB is ready${NC}"

# Wait for backend API to respond
echo -e "${YELLOW}🌐 Waiting for backend API...${NC}"
until curl -sf http://localhost:8001/api/v1/health/ > /dev/null 2>&1; do
    echo "Waiting for backend health endpoint..."
    sleep 3
done
echo -e "${GREEN}✅ Backend API is responding${NC}"

# Add initial GitHub repository for monitoring
echo -e "${YELLOW}📚 Adding GitHub repository for monitoring...${NC}"
docker-compose -f docker-compose.test.yml exec -T backend python manage.py add_github_repo 0xMarcio/cve --frequency 1hour || true

# Run initial scrape
echo -e "${YELLOW}🕷️  Running initial ransomware.live scrape...${NC}"
docker-compose -f docker-compose.test.yml exec -T backend python manage.py scrape_ransomware_live || true

# Check if services are running
echo -e "${YELLOW}🔍 Checking service status...${NC}"
docker-compose -f docker-compose.test.yml ps

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📋 Service URLs:"
echo "   - Frontend: http://localhost:3001"
echo "   - Backend API: http://localhost:8001/api/v1"
echo "   - Admin Panel: http://localhost:8001/admin"
echo "   - API Docs: http://localhost:8001/api/v1/"
echo ""
echo "🧪 To run tests:"
echo "   docker-compose -f docker-compose.test.yml exec backend python manage.py test"
echo ""
echo "📊 To view logs:"
echo "   docker-compose -f docker-compose.test.yml logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.test.yml down"

