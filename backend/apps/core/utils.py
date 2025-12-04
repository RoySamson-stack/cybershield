"""Utility functions for core app"""
import secrets
from django.utils import timezone
from datetime import timedelta
from .models import APIKey, UsageMetrics, Subscription


def generate_api_key():
    """Generate a secure API key"""
    key = secrets.token_urlsafe(32)
    key_prefix = key[:8]
    return key, key_prefix


def track_usage(organization, metric_type, count=1, api_key=None, metadata=None):
    """Track usage metrics for billing"""
    from datetime import date
    
    today = date.today()
    metadata = metadata or {}
    
    usage, created = UsageMetrics.objects.get_or_create(
        organization=organization,
        api_key=api_key,
        metric_type=metric_type,
        date=today,
        defaults={'count': count, 'metadata': metadata}
    )
    
    if not created:
        usage.count += count
        if metadata:
            usage.metadata.update(metadata)
        usage.save()
    
    return usage


def check_usage_limit(organization, metric_type):
    """Check if organization is within usage limits"""
    subscription = organization.subscription
    if not subscription:
        return False, 0, 0
    
    from datetime import date
    from django.db.models import Sum
    
    today = date.today()
    usage = UsageMetrics.objects.filter(
        organization=organization,
        metric_type=metric_type,
        date__year=today.year,
        date__month=today.month
    ).aggregate(total=Sum('count'))['total'] or 0
    
    limit_map = {
        'scan': subscription.max_scans_per_month,
        'api_request': subscription.max_api_requests_per_month,
    }
    
    limit = limit_map.get(metric_type, -1)
    if limit == -1:  # Unlimited
        return True, usage, limit
    
    return usage < limit, usage, limit


def get_subscription_features(subscription):
    """Get list of enabled features for a subscription"""
    if not subscription:
        return []
    
    features = []
    if subscription.has_api_access:
        features.append('api_access')
    if subscription.has_webhooks:
        features.append('webhooks')
    if subscription.has_priority_support:
        features.append('priority_support')
    if subscription.has_custom_integrations:
        features.append('custom_integrations')
    if subscription.has_advanced_analytics:
        features.append('advanced_analytics')
    
    return features


def create_trial_subscription(organization):
    """Create a trial subscription for a new organization"""
    subscription = Subscription.objects.create(
        plan_type='free',
        billing_cycle='monthly',
        price=0.00,
        max_scans_per_month=100,
        max_api_requests_per_month=10000,
        max_monitored_domains=5,
        max_alert_rules=10,
        retention_days=30,
        status='trial',
        current_period_start=timezone.now(),
        current_period_end=timezone.now() + timedelta(days=30)
    )
    
    organization.subscription = subscription
    organization.save()
    
    return subscription

