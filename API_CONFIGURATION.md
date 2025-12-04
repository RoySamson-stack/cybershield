# API Configuration Guide

## Overview
CyberShield is a cybersecurity community platform where professionals share threat intelligence, ransomware groups, breaches, C2 servers, and other cybersecurity information.

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.cybershield.io/api/v1
```

## Authentication
All API requests require authentication via JWT tokens:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### Threat Intelligence
- **GET** `/threats/threat-intelligence/` - List all threat intelligence posts
- **POST** `/threats/threat-intelligence/` - Share new threat intelligence
- **GET** `/threats/threat-intelligence/{id}/` - Get specific threat
- **GET** `/threats/threat-intelligence/map_data/` - Get geographic distribution data

**Query Parameters:**
- `threat_type`: Filter by type (ransomware, data_breach, phishing, c2, malware, apt)
- `severity`: Filter by severity (critical, high, medium, low)
- `page`: Page number for pagination
- `page_size`: Items per page

### Ransomware
- **GET** `/ransomware/groups/` - List ransomware groups
- **POST** `/ransomware/groups/` - Share new ransomware group
- **GET** `/ransomware/groups/{id}/` - Get specific group
- **GET** `/ransomware/incidents/` - List ransomware incidents
- **POST** `/ransomware/incidents/` - Share new incident

**Query Parameters:**
- `threat_level`: Filter by threat level
- `active`: Filter by active status (true/false)
- `name`: Search by group name

### Data Breaches
- **GET** `/breaches/` - List data breaches
- **POST** `/breaches/` - Share new breach
- **GET** `/breaches/{id}/` - Get specific breach
- **GET** `/breaches/stats/` - Get breach statistics

**Query Parameters:**
- `industry`: Filter by industry
- `status`: Filter by status (confirmed, unconfirmed)
- `organization`: Search by organization name

### C2 Servers
- **GET** `/threats/c2-servers/` - List C2 servers
- **POST** `/threats/c2-servers/` - Share new C2 server
- **GET** `/threats/c2-servers/{id}/` - Get specific C2 server
- **GET** `/threats/c2-servers/stats/` - Get C2 server statistics

**Query Parameters:**
- `threat_level`: Filter by threat level
- `c2_family`: Filter by C2 family
- `country`: Filter by country
- `is_active`: Filter by active status

### Onion Sites
- **GET** `/threats/onion-sites/` - List onion sites
- **POST** `/threats/onion-sites/` - Share new onion site
- **GET** `/threats/onion-sites/{id}/` - Get specific site
- **GET** `/threats/onion-posts/` - List data posts on onion sites
- **POST** `/threats/onion-posts/` - Share new data post

**Query Parameters:**
- `site_type`: Filter by site type (ransomware, marketplace, forum)
- `status`: Filter by status (active, inactive)
- `onion_address`: Search by onion address

### Leaked Credentials
- **GET** `/threats/leaked-credentials/` - List leaked credentials
- **POST** `/threats/leaked-credentials/` - Share new credential leak
- **GET** `/threats/leaked-credentials/{id}/` - Get specific credential
- **GET** `/threats/leaked-credentials/search/` - Search credentials
- **GET** `/threats/leaked-credentials/stats/` - Get credential statistics

**Query Parameters:**
- `email`: Search by email
- `domain`: Filter by domain
- `breach_source`: Filter by breach source
- `is_exposed`: Filter by exposure status

### Phishing
- **GET** `/phishing/campaigns/` - List phishing campaigns
- **POST** `/phishing/campaigns/` - Share new campaign
- **GET** `/phishing/domains/` - List phishing domains
- **POST** `/phishing/domains/` - Share new domain

### Security Scanner
- **GET** `/scanner/targets/` - List scan targets
- **POST** `/scanner/targets/` - Create new scan target
- **GET** `/scanner/scans/` - List security scans
- **POST** `/scanner/scans/` - Start new scan
- **GET** `/scanner/vulnerabilities/` - List vulnerabilities

### Alerts
- **GET** `/alerts/` - List alerts
- **POST** `/alerts/` - Create new alert
- **GET** `/alerts/rules/` - List alert rules
- **POST** `/alerts/rules/` - Create alert rule

## Response Format

### Success Response
```json
{
  "count": 100,
  "next": "http://api.cybershield.io/api/v1/threats/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

## Frontend API Client

The frontend uses a configured axios instance in `frontend/lib/api.ts`:

- **Base URL**: Configured via `NEXT_PUBLIC_API_URL` environment variable
- **Authentication**: Automatically adds JWT token from localStorage
- **Caching**: GET requests are cached for 5 minutes
- **Token Refresh**: Automatically refreshes expired tokens
- **Error Handling**: Handles 401 errors and redirects to login

## Demo Mode

For frontend development without backend:
- Set `is_demo: true` in localStorage
- Frontend will use mock data instead of API calls
- All pages support demo mode with realistic sample data

## Environment Variables

```bash
# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Backend
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

