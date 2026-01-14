#!/bin/bash

set -e

echo "🔧 Setting up GitHub CVE Monitoring"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

REPO="${1:-0xMarcio/cve}"
FREQUENCY="${2:-1hour}"

echo -e "${YELLOW}Adding GitHub repository: ${REPO}${NC}"
echo -e "${YELLOW}Monitoring frequency: ${FREQUENCY}${NC}"
echo ""

# Add the GitHub repository
docker-compose exec -T backend python manage.py add_github_repo "$REPO" --frequency "$FREQUENCY"

echo ""
echo -e "${YELLOW}Triggering initial check to pull CVE data...${NC}"
echo ""

# Get the repo ID and trigger a check
REPO_ID=$(docker-compose exec -T backend python manage.py shell -c "
from apps.monitoring.models import GitHubRepository
repo = GitHubRepository.objects.get(full_name='$REPO')
print(repo.id)
" | tr -d '\r\n')

if [ -n "$REPO_ID" ]; then
    echo -e "${GREEN}Repository ID: ${REPO_ID}${NC}"
    echo ""
    echo -e "${YELLOW}Triggering manual check...${NC}"
    docker-compose exec -T backend python manage.py shell -c "
from apps.monitoring.tasks import monitor_github_repository
monitor_github_repository.delay('$REPO_ID')
print('Check queued successfully!')
"
    echo ""
    echo -e "${GREEN}✅ Setup complete!${NC}"
    echo ""
    echo "The repository will be monitored automatically by Celery Beat."
    echo "You can also trigger manual checks from the frontend CVE page."
    echo ""
    echo "To check status:"
    echo "  docker-compose exec backend python manage.py shell -c \"from apps.monitoring.models import GitHubRepository; r = GitHubRepository.objects.get(full_name='$REPO'); print(f'Last check: {r.last_check_at}, CVEs found: {r.total_cves_found}')\""
else
    echo -e "${RED}❌ Failed to get repository ID${NC}"
    exit 1
fi

