# CyberShield Intelligence Platform

Enterprise-grade cybersecurity intelligence platform combining ransomware monitoring, breach aggregation, security scanning, phishing detection, and comprehensive threat intelligence.

##  Features

### Core Capabilities
- **Ransomware Monitoring**: Track threat actor groups and incidents in real-time
- **Data Breach Aggregation**: Monitor and alert on data breaches
- **Security Scanning**: Vulnerability assessment, SSL/TLS scanning, port scanning
- **Phishing Detection**: Domain and campaign monitoring
- **Alert System**: Configurable notifications via email, webhooks, Slack, Teams

### Enterprise Features
- **Multi-Tenancy**: Organization-based data isolation
- **Subscription Management**: Flexible billing with Stripe integration
- **API Access**: Secure API key authentication with rate limiting
- **Usage Tracking**: Real-time monitoring of API calls and resource usage
- **Audit Logging**: Comprehensive activity tracking for compliance
- **Role-Based Access Control**: Owner, Admin, Member, Viewer roles

## 📋 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM

### Development Setup

```bash
# Clone repository
git clone  https://github.com/RoySamson-stack/cybershield.git
cd cybershield

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Create subscription plans
docker-compose exec backend python manage.py create_subscription_plans
```

### Access Points
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001/api/v1
- **Admin Panel**: http://localhost:8001/admin
- **API Docs**: http://localhost:8001/api/docs (if enabled)
- **Health Check**: http://localhost:8001/api/v1/health/

### Production Deployment

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --no-input
```

## 🏗️ Architecture

### Tech Stack
- **Backend**: Django 5.0, Django REST Framework, Celery
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS
- **Databases**: PostgreSQL, MongoDB, Redis
- **Infrastructure**: Docker, Nginx, Prometheus, Grafana

### Services
- `backend`: Django REST API
- `frontend`: Next.js application
- `postgres`: PostgreSQL database
- `mongodb`: MongoDB document store
- `redis`: Redis cache and message broker
- `celery_worker`: Background task processor
- `celery_beat`: Scheduled task scheduler
- `nginx`: Reverse proxy and load balancer
- `prometheus`: Metrics collection
- `grafana`: Metrics visualization

## 💰 Monetization

### Subscription Plans

| Plan | Price | Scans/Month | API Requests/Month | Features |
|------|-------|-------------|-------------------|----------|
| **Free** | $0 | 100 | 10,000 | Basic monitoring |
| **Starter** | $49/mo | 1,000 | 100,000 | API access, email support |
| **Professional** | $199/mo | 10,000 | 1,000,000 | Webhooks, priority support |
| **Enterprise** | Custom | Unlimited | Unlimited | Custom integrations, SLA |

See [ENTERPRISE_FEATURES.md](./ENTERPRISE_FEATURES.md) for detailed feature comparison.

## 📚 Documentation

- [Enterprise Features](./ENTERPRISE_FEATURES.md): Comprehensive feature documentation
- [Deployment Guide](./DEPLOYMENT.md): Production deployment instructions
- [API Documentation](./docs/API.md): API reference (coming soon)
- [User Guide](./docs/USER_GUIDE.md): User documentation (coming soon)

## 🔒 Security

- JWT and API key authentication
- Rate limiting and DDoS protection
- Comprehensive audit logging
- Role-based access control
- Data encryption at rest and in transit
- Security headers (XSS, CSRF protection)
- Input validation and sanitization

## 📊 Monitoring

- Health check endpoints
- Prometheus metrics export
- Grafana dashboards
- Structured logging
- Performance monitoring
- Error tracking with Sentry

## 🛠️ Development

### Running Tests
```bash
docker-compose exec backend python manage.py test
```

### Code Quality
```bash
# Backend
docker-compose exec backend black .
docker-compose exec backend flake8 .

# Frontend
docker-compose exec frontend npm run lint
```

### Database Migrations
```bash
# Create migrations
docker-compose exec backend python manage.py makemigrations

# Apply migrations
docker-compose exec backend python manage.py migrate
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

[Your License Here]

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/cybershield/issues)
- **Email**: support@cybershield.com
- **Documentation**: [Full Docs](./docs/)

## 🗺️ Roadmap

- [x] Multi-tenancy and organizations
- [x] Subscription and billing system
- [x] API key management
- [x] Basic monitoring features
- [ ] Advanced analytics dashboard
- [ ] Machine learning threat detection
- [ ] Custom integrations (Slack, Teams)
- [ ] Mobile application
- [ ] Threat intelligence feeds
- [ ] Automated remediation
- [ ] Compliance reporting

---