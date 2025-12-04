"""Business logic services for core features"""
from django.utils import timezone
from datetime import timedelta
from .models import Organization, Subscription, UsageMetrics
from .utils import check_usage_limit, track_usage


class BillingService:
    """Service for handling billing and usage"""
    
    @staticmethod
    def check_and_track_usage(organization, metric_type, count=1, api_key=None, metadata=None):
        """Check usage limit and track usage"""
        within_limit, current_usage, limit = check_usage_limit(organization, metric_type)
        
        if not within_limit:
            return {
                'allowed': False,
                'message': f'Usage limit exceeded for {metric_type}. Limit: {limit}, Used: {current_usage}',
                'current_usage': current_usage,
                'limit': limit
            }
        
        # Track usage
        track_usage(organization, metric_type, count, api_key, metadata)
        
        return {
            'allowed': True,
            'current_usage': current_usage + count,
            'limit': limit,
            'remaining': limit - (current_usage + count) if limit != -1 else -1
        }
    
    @staticmethod
    def get_usage_summary(organization, start_date=None, end_date=None):
        """Get usage summary for an organization"""
        from django.db.models import Sum
        from datetime import date
        
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
        
        usage = UsageMetrics.objects.filter(
            organization=organization,
            date__gte=start_date,
            date__lte=end_date
        ).values('metric_type').annotate(total=Sum('count'))
        
        return {item['metric_type']: item['total'] for item in usage}
    
    @staticmethod
    def calculate_usage_cost(organization, metric_type, count):
        """Calculate cost for usage (for future billing)"""
        # This would integrate with Stripe for usage-based billing
        # For now, return 0 as subscriptions are flat-rate
        return 0.00


class SubscriptionService:
    """Service for managing subscriptions"""
    
    @staticmethod
    def upgrade_subscription(organization, new_plan_type, billing_cycle='monthly'):
        """Upgrade organization subscription"""
        try:
            new_subscription = Subscription.objects.get(
                plan_type=new_plan_type,
                billing_cycle=billing_cycle,
                status='active'
            )
        except Subscription.DoesNotExist:
            return {'success': False, 'error': 'Subscription plan not found'}
        
        old_subscription = organization.subscription
        
        # Update organization subscription
        organization.subscription = new_subscription
        organization.save()
        
        # Here you would integrate with Stripe to create/update subscription
        # For now, just update the database
        
        return {
            'success': True,
            'old_plan': old_subscription.plan_type if old_subscription else None,
            'new_plan': new_subscription.plan_type,
            'message': f'Subscription upgraded to {new_plan_type}'
        }
    
    @staticmethod
    def cancel_subscription(organization):
        """Cancel subscription at period end"""
        subscription = organization.subscription
        if not subscription:
            return {'success': False, 'error': 'No active subscription'}
        
        subscription.cancel_at_period_end = True
        subscription.save()
        
        return {
            'success': True,
            'message': f'Subscription will be cancelled on {subscription.current_period_end}',
            'cancel_date': subscription.current_period_end
        }
    
    @staticmethod
    def renew_subscription(organization):
        """Renew subscription for next period"""
        subscription = organization.subscription
        if not subscription:
            return {'success': False, 'error': 'No active subscription'}
        
        # Calculate next period
        if subscription.billing_cycle == 'monthly':
            period_delta = timedelta(days=30)
        else:  # yearly
            period_delta = timedelta(days=365)
        
        subscription.current_period_start = timezone.now()
        subscription.current_period_end = timezone.now() + period_delta
        subscription.cancel_at_period_end = False
        subscription.status = 'active'
        subscription.save()
        
        return {
            'success': True,
            'next_period_end': subscription.current_period_end,
            'message': 'Subscription renewed successfully'
        }

