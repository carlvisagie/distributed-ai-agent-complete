#!/bin/bash
set -euo pipefail

echo "=== Distributed AI Agent System - Quick Deploy ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env file with your configuration:${NC}"
    echo "   - Set RUNNER_MODE (mock or openhands)"
    echo "   - Set LLM_API_KEY if using openhands mode"
    echo "   - Set GITHUB_TOKEN for PR workflow"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Verify critical settings
source .env

if [ "$RUNNER_MODE" == "openhands" ] && [ -z "${LLM_API_KEY:-}" ]; then
    echo -e "${RED}❌ RUNNER_MODE is 'openhands' but LLM_API_KEY is not set${NC}"
    echo "   Please set LLM_API_KEY in .env file"
    exit 1
fi

echo -e "${GREEN}✅ Configuration validated${NC}"
echo ""

# Build and start services
echo "Building Docker images..."
docker compose build

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Health checks
echo ""
echo "Running health checks..."

OMEN_HEALTH=$(curl -s http://localhost:8080/health || echo "failed")
if [[ "$OMEN_HEALTH" == *"healthy"* ]]; then
    echo -e "${GREEN}✅ HP OMEN Orchestrator: healthy${NC}"
else
    echo -e "${RED}❌ HP OMEN Orchestrator: unhealthy${NC}"
fi

LENOVO_HEALTH=$(curl -s http://localhost:8088/healthz || echo "failed")
if [[ "$LENOVO_HEALTH" == *"ok"* ]]; then
    echo -e "${GREEN}✅ Lenovo API: healthy${NC}"
else
    echo -e "${RED}❌ Lenovo API: unhealthy${NC}"
fi

# Check database
DB_CHECK=$(docker compose exec -T lenovo-db psql -U agent -d agentops -c "SELECT 1;" 2>&1 || echo "failed")
if [[ "$DB_CHECK" == *"1 row"* ]]; then
    echo -e "${GREEN}✅ PostgreSQL: healthy${NC}"
else
    echo -e "${RED}❌ PostgreSQL: unhealthy${NC}"
fi

# Check Redis
REDIS_CHECK=$(docker compose exec -T lenovo-redis redis-cli ping 2>&1 || echo "failed")
if [[ "$REDIS_CHECK" == "PONG" ]]; then
    echo -e "${GREEN}✅ Redis: healthy${NC}"
else
    echo -e "${RED}❌ Redis: unhealthy${NC}"
fi

echo ""
echo "=== Deployment Complete ==="
echo ""
echo -e "${GREEN}🎉 System is running!${NC}"
echo ""
echo "Access points:"
echo "  - Chat Interface: http://localhost"
echo "  - HP OMEN API: http://localhost:8080"
echo "  - Lenovo API: http://localhost:8088"
echo ""
echo "Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop system: docker compose down"
echo "  - Restart: docker compose restart"
echo ""
echo "Mode: $RUNNER_MODE"
if [ "$RUNNER_MODE" == "mock" ]; then
    echo -e "${YELLOW}ℹ️  Running in MOCK mode (no API key required)${NC}"
else
    echo -e "${GREEN}✅ Running in OPENHANDS mode (real AI execution)${NC}"
fi
echo ""
