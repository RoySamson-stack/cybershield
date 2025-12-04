# CyberShield Deployment Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- 20GB+ disk space

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd cybershield
cp .env.example .env
# Edit .env with your configuration
```

### 2. Development Deployment

```bash
# Build and start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Create initial subscription plans
docker-compose exec backend python manage.py create_subscription_plans
```

### 3. Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --no-input

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Environment Configuration

### Required Variables

```bash
# Django
DJANGO_SECRET_KEY=<generate-secure-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
POSTGRES_DB=cybershield
POSTGRES_USER=cybershield
POSTGRES_PASSWORD=<strong-password>

# MongoDB
MONGODB_USER=cybershield
MONGODB_PASSWORD=<strong-password>
MONGODB_DB=cybershield

# Redis
REDIS_PASSWORD=<strong-password>

# Stripe (for billing)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## SSL/TLS Setup

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/
```

### Update Nginx Config

Edit `docker/nginx/nginx.conf` to enable HTTPS:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    # ... rest of config
}
```

## Database Backups

### PostgreSQL Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U cybershield cybershield > backup.sql

# Restore
docker-compose exec -T postgres psql -U cybershield cybershield < backup.sql
```

### MongoDB Backup

```bash
# Backup
docker-compose exec mongodb mongodump --out /backup

# Restore
docker-compose exec mongodb mongorestore /backup
```

## Monitoring

### Access Dashboards

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### Health Checks

```bash
# API health
curl http://localhost/api/v1/health/

# Service status
docker-compose ps
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend workers
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=4
```

### Resource Limits

Edit `docker-compose.prod.yml` to adjust resource limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

## Troubleshooting

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Database Issues

```bash
# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up regular backups
- [ ] Enable monitoring and alerts
- [ ] Review and restrict CORS origins
- [ ] Set up rate limiting
- [ ] Configure security headers
- [ ] Enable audit logging

## Performance Optimization

1. **Enable Redis caching**: Already configured
2. **Database indexing**: Run `python manage.py create_indexes`
3. **Static file CDN**: Use CloudFront/Cloudflare
4. **Database connection pooling**: Configured in settings
5. **Celery optimization**: Adjust worker concurrency

## Maintenance

### Regular Tasks

```bash
# Update dependencies
docker-compose build --no-cache

# Clean up old logs
docker-compose exec backend python manage.py cleanup_logs

# Optimize database
docker-compose exec postgres psql -U cybershield -c "VACUUM ANALYZE;"
```

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Email: support@cybershield.com
- Documentation: /docs

