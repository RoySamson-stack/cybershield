#!/bin/bash

set -e

echo "🧪 CyberShield Full System Test"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_status)"
        ((FAILED++))
        return 1
    fi
}

# Function to test service health
test_service() {
    local service=$1
    echo -n "Checking $service container... "
    if docker-compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✓ RUNNING${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ NOT RUNNING${NC}"
        ((FAILED++))
    fi
}

echo -e "${BLUE}📋 Checking Docker Services...${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

# Check if containers are running
test_service "cybershield_backend"
test_service "cybershield_postgres"
test_service "cybershield_mongodb"
test_service "cybershield_redis"
test_service "cybershield_frontend"

echo ""
echo -e "${BLUE}🌐 Testing API Endpoints...${NC}"
echo ""

# Wait a bit for services to be ready
sleep 2

# Test health endpoint
test_endpoint "Health Check" "http://localhost:8001/api/v1/health/" 200

# Test API root
test_endpoint "API Root" "http://localhost:8001/api/v1/" 200

# Test authentication endpoints
test_endpoint "Login Endpoint" "http://localhost:8001/api/v1/auth/login/" 405  # Method not allowed for GET is OK

# Test core endpoints
test_endpoint "Organizations" "http://localhost:8001/api/v1/organizations/" 401  # Unauthorized is expected without auth

# Test ransomware endpoints
test_endpoint "Ransomware Groups" "http://localhost:8001/api/v1/ransomware/groups/" 401

# Test breaches endpoints
test_endpoint "Data Breaches" "http://localhost:8001/api/v1/breaches/" 401

# Test scanner endpoints
test_endpoint "Scanner" "http://localhost:8001/api/v1/scanner/" 401

# Test phishing endpoints
test_endpoint "Phishing" "http://localhost:8001/api/v1/phishing/" 401

# Test CVE endpoints
test_endpoint "CVE" "http://localhost:8001/api/v1/cve/" 401

echo ""
echo -e "${BLUE}🔍 Testing Database Connections...${NC}"
echo ""

# Test PostgreSQL
echo -n "PostgreSQL connection... "
if docker-compose exec -T postgres pg_isready -U cybershield > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CONNECTED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test MongoDB
echo -n "MongoDB connection... "
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CONNECTED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test Redis
echo -n "Redis connection... "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CONNECTED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}🖥️  Testing Frontend...${NC}"
echo ""

# Test frontend
test_endpoint "Frontend" "http://localhost:3001" 200

echo ""
echo -e "${BLUE}📊 Testing Celery Workers...${NC}"
echo ""

# Check Celery worker
echo -n "Celery worker... "
if docker-compose ps | grep -q "celery_worker.*Up"; then
    echo -e "${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ NOT RUNNING (optional)${NC}"
fi

# Check Celery beat
echo -n "Celery beat... "
if docker-compose ps | grep -q "celery_beat.*Up"; then
    echo -e "${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ NOT RUNNING (optional)${NC}"
fi

echo ""
echo -e "${BLUE}📝 Testing Admin Panel...${NC}"
echo ""

# Test admin panel
test_endpoint "Admin Panel" "http://localhost:8001/admin/" 200

echo ""
echo "================================"
echo -e "${BLUE}📈 Test Summary${NC}"
echo "================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All critical tests passed!${NC}"
    echo ""
    echo "🌐 Access your application:"
    echo "   - Frontend: http://localhost:3001"
    echo "   - Backend API: http://localhost:8001/api/v1"
    echo "   - Admin Panel: http://localhost:8001/admin"
    echo ""
    echo "📚 Next steps:"
    echo "   1. Create a superuser: docker-compose exec backend python manage.py createsuperuser"
    echo "   2. Create subscription plans: docker-compose exec backend python manage.py create_subscription_plans"
    echo "   3. Access the frontend and create an account"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the logs:${NC}"
    echo "   docker-compose logs"
    exit 1
fi

