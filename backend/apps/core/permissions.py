from rest_framework import permissions


class IsOrganizationMember(permissions.BasePermission):
    """Permission to check if user belongs to organization"""
    
    def has_permission(self, request, view):
        if not hasattr(request, 'organization') or not request.organization:
            return False
        
        if request.user.is_authenticated:
            return request.user.organization == request.organization
        
        if hasattr(request, 'api_key') and request.api_key:
            return request.api_key.organization == request.organization
        
        return False


class IsOrganizationOwner(permissions.BasePermission):
    """Permission to check if user is organization owner"""
    
    def has_permission(self, request, view):
        if not hasattr(request, 'organization') or not request.organization:
            return False
        
        if request.user.is_authenticated:
            return (
                request.user.organization == request.organization and
                request.user.role in ['owner', 'admin']
            )
        
        return False


class HasAPIAccess(permissions.BasePermission):
    """Permission to check if organization has API access"""
    
    def has_permission(self, request, view):
        if not hasattr(request, 'organization') or not request.organization:
            return False
        
        subscription = request.organization.subscription
        if not subscription:
            return False
        
        return subscription.has_api_access


class HasFeatureAccess(permissions.BasePermission):
    """Permission to check if organization has access to a specific feature"""
    
    def __init__(self, feature_name):
        self.feature_name = feature_name
    
    def has_permission(self, request, view):
        if not hasattr(request, 'organization') or not request.organization:
            return False
        
        subscription = request.organization.subscription
        if not subscription:
            return False
        
        feature_map = {
            'webhooks': 'has_webhooks',
            'priority_support': 'has_priority_support',
            'custom_integrations': 'has_custom_integrations',
            'advanced_analytics': 'has_advanced_analytics',
        }
        
        feature_attr = feature_map.get(self.feature_name)
        if not feature_attr:
            return False
        
        return getattr(subscription, feature_attr, False)


class IsWithinUsageLimit(permissions.BasePermission):
    """Permission to check if organization is within usage limits"""
    
    def __init__(self, metric_type):
        self.metric_type = metric_type
    
    def has_permission(self, request, view):
        if not hasattr(request, 'organization') or not request.organization:
            return False
        
        subscription = request.organization.subscription
        if not subscription:
            return False
        
        from django.utils import timezone
        from datetime import date
        from django.db.models import Sum
        from .models import UsageMetrics
        
        # Get current month usage
        today = date.today()
        usage = UsageMetrics.objects.filter(
            organization=request.organization,
            metric_type=self.metric_type,
            date__year=today.year,
            date__month=today.month
        ).aggregate(total=Sum('count'))['total'] or 0
        
        # Check limit based on metric type
        limit_map = {
            'scan': subscription.max_scans_per_month,
            'api_request': subscription.max_api_requests_per_month,
        }
        
        limit = limit_map.get(self.metric_type, -1)
        if limit == -1:  # Unlimited
            return True
        
        return usage < limit

