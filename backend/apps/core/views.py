from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import HealthCheck
import os


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring"""
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'services': {}
    }
    
    # Check database
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check Redis
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['services']['redis'] = 'healthy'
        else:
            health_status['services']['redis'] = 'unhealthy'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check MongoDB (if configured)
    try:
        from pymongo import MongoClient
        from django.conf import settings
        client = MongoClient(
            host=settings.MONGODB_CONFIG['host'],
            port=settings.MONGODB_CONFIG['port'],
            username=settings.MONGODB_CONFIG.get('username'),
            password=settings.MONGODB_CONFIG.get('password'),
            serverSelectionTimeoutMS=5000
        )
        client.server_info()
        health_status['services']['mongodb'] = 'healthy'
    except Exception as e:
        health_status['services']['mongodb'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # System metrics
    try:
        import psutil
        health_status['system'] = {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }
    except (ImportError, Exception):
        pass
    
    # Save health check record
    try:
        HealthCheck.objects.create(
            service_name='api',
            status=health_status['status'],
            metadata=health_status
        )
    except Exception:
        pass
    
    http_status = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(health_status, status=http_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def metrics(request):
    """Prometheus metrics endpoint"""
    from django_prometheus.middleware import PrometheusAfterMiddleware
    from django.http import HttpResponse
    
    # This would typically be handled by django-prometheus
    # For now, return basic metrics
    metrics_data = "# HELP http_requests_total Total number of HTTP requests\n"
    metrics_data += "# TYPE http_requests_total counter\n"
    
    return HttpResponse(metrics_data, content_type='text/plain')
