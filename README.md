# CyberShield Intelligence Platform

Complete cybersecurity intelligence platform combining ransomware monitoring, breach aggregation, security scanning, and more.

## Quick Start

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1
# Admin: http://localhost:8000/admin
```

## Documentation

See `/docs` for detailed documentation.
# cybershield
# cybershield
