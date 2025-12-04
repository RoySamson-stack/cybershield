from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone
from .models import Organization, APIKey, UsageMetrics, AuditLog
import re


class OrganizationMiddleware(MiddlewareMixin):
    """Multi-tenancy middleware to set organization context"""
    
    def process_request(self, request):
        request.organization = None
        
        # Get organization from authenticated user
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'organization') and request.user.organization:
                request.organization = request.user.organization
        
        # Get organization from API key
        elif hasattr(request, 'api_key') and request.api_key:
            request.organization = request.api_key.organization
        
        # Get organization from subdomain or header
        else:
            # Check for organization header
            org_slug = request.headers.get('X-Organization-Slug')
            if org_slug:
                try:
                    request.organization = Organization.objects.get(
                        slug=org_slug,
                        is_active=True
                    )
                except Organization.DoesNotExist:
                    pass
        
        return None


class APIKeyMiddleware(MiddlewareMixin):
    """Middleware to authenticate requests using API keys"""
    
    def process_request(self, request):
        request.api_key = None
        
        # Skip authentication for certain paths
        skip_paths = [
            '/api/v1/auth/',
            '/admin/',
            '/health/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Check for API key in header
        api_key_header = request.headers.get('X-API-Key') or request.headers.get('Authorization')
        
        if api_key_header:
            # Handle Bearer token format
            if api_key_header.startswith('Bearer '):
                api_key_value = api_key_header[7:]
            else:
                api_key_value = api_key_header
            
            try:
                api_key = APIKey.objects.select_related('organization').get(
                    key=api_key_value,
                    is_active=True
                )
                
                # Check if expired
                if api_key.is_expired():
                    return JsonResponse(
                        {'error': 'API key has expired'},
                        status=401
                    )
                
                # Check rate limiting
                if not self._check_rate_limit(api_key):
                    return JsonResponse(
                        {'error': 'Rate limit exceeded'},
                        status=429
                    )
                
                # Update last used
                api_key.last_used_at = timezone.now()
                api_key.last_used_ip = self._get_client_ip(request)
                api_key.save(update_fields=['last_used_at', 'last_used_ip'])
                
                # Track usage
                self._track_usage(api_key, request)
                
                request.api_key = api_key
                request.user = None  # API key requests don't have a user
                
            except APIKey.DoesNotExist:
                return JsonResponse(
                    {'error': 'Invalid API key'},
                    status=401
                )
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _check_rate_limit(self, api_key):
        """Check if API key is within rate limit"""
        from django.core.cache import cache
        
        cache_key = f'api_rate_limit:{api_key.id}'
        current_count = cache.get(cache_key, 0)
        
        if current_count >= api_key.rate_limit_per_hour:
            return False
        
        cache.set(cache_key, current_count + 1, 3600)  # 1 hour TTL
        return True
    
    def _track_usage(self, api_key, request):
        """Track API usage for billing"""
        from datetime import date
        
        UsageMetrics.objects.create(
            organization=api_key.organization,
            api_key=api_key,
            metric_type='api_request',
            metadata={
                'path': request.path,
                'method': request.method,
            },
            date=date.today()
        )


class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to log API requests for audit purposes"""
    
    def process_response(self, request, response):
        # Only log API requests
        if not request.path.startswith('/api/'):
            return response
        
        # Skip if no organization context
        if not hasattr(request, 'organization') or not request.organization:
            return response
        
        # Create audit log asynchronously (use Celery in production)
        try:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            api_key = request.api_key if hasattr(request, 'api_key') and request.api_key else None
            
            AuditLog.objects.create(
                organization=request.organization,
                user=user,
                api_key=api_key,
                action_type='api_call',
                resource_type='api',
                resource_id=request.path,
                description=f"{request.method} {request.path}",
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={
                    'status_code': response.status_code,
                    'method': request.method,
                }
            )
        except Exception:
            # Don't fail the request if audit logging fails
            pass
        
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

