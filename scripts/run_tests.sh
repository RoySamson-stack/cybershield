#!/bin/bash

set -e

echo "🧪 Running CyberShield Tests"
echo "============================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if services are running
if ! docker-compose -f docker-compose.test.yml ps | grep -q "Up"; then
    echo -e "${RED}❌ Services are not running. Please run ./scripts/test_setup.sh first.${NC}"
    exit 1
fi

# Run Django tests
echo -e "${YELLOW}🔬 Running Django tests...${NC}"
docker-compose -f docker-compose.test.yml exec -T backend python manage.py test --verbosity=2

# Run specific app tests
echo -e "${YELLOW}🔬 Running CVE app tests...${NC}"
docker-compose -f docker-compose.test.yml exec -T backend python manage.py test apps.cve --verbosity=2 || true

echo -e "${YELLOW}🔬 Running Monitoring app tests...${NC}"
docker-compose -f docker-compose.test.yml exec -T backend python manage.py test apps.monitoring --verbosity=2 || true

# Check API health
echo -e "${YELLOW}🏥 Checking API health...${NC}"
HEALTH_CHECK=$(curl -s http://localhost:8000/api/v1/health/ || echo "FAILED")
if [[ "$HEALTH_CHECK" == *"status"* ]]; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API health check failed${NC}"
fi

# Test API endpoints
echo -e "${YELLOW}🌐 Testing API endpoints...${NC}"

# Test CVE endpoint
echo "Testing CVE endpoint..."
curl -s http://localhost:8000/api/v1/cve/cves/ | head -c 100 && echo "..." || echo "Failed"

# Test Monitoring endpoints
echo "Testing Monitoring endpoints..."
curl -s http://localhost:8000/api/v1/monitoring/github-repos/ | head -c 100 && echo "..." || echo "Failed"

echo ""
echo -e "${GREEN}✅ Tests complete!${NC}"

