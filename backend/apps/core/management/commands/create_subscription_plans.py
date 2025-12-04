from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Subscription


class Command(BaseCommand):
    help = 'Create default subscription plans'

    def handle(self, *args, **options):
        plans = [
            {
                'plan_type': 'free',
                'billing_cycle': 'monthly',
                'price': 0.00,
                'max_scans_per_month': 100,
                'max_api_requests_per_month': 10000,
                'max_monitored_domains': 5,
                'max_alert_rules': 10,
                'retention_days': 30,
                'has_api_access': False,
                'has_webhooks': False,
                'has_priority_support': False,
                'has_custom_integrations': False,
                'has_advanced_analytics': False,
                'status': 'active',
            },
            {
                'plan_type': 'starter',
                'billing_cycle': 'monthly',
                'price': 49.00,
                'max_scans_per_month': 1000,
                'max_api_requests_per_month': 100000,
                'max_monitored_domains': 25,
                'max_alert_rules': 50,
                'retention_days': 90,
                'has_api_access': True,
                'has_webhooks': False,
                'has_priority_support': False,
                'has_custom_integrations': False,
                'has_advanced_analytics': False,
                'status': 'active',
            },
            {
                'plan_type': 'professional',
                'billing_cycle': 'monthly',
                'price': 199.00,
                'max_scans_per_month': 10000,
                'max_api_requests_per_month': 1000000,
                'max_monitored_domains': 100,
                'max_alert_rules': -1,  # Unlimited
                'retention_days': 365,
                'has_api_access': True,
                'has_webhooks': True,
                'has_priority_support': True,
                'has_custom_integrations': False,
                'has_advanced_analytics': True,
                'status': 'active',
            },
            {
                'plan_type': 'enterprise',
                'billing_cycle': 'monthly',
                'price': 999.00,
                'max_scans_per_month': -1,  # Unlimited
                'max_api_requests_per_month': -1,  # Unlimited
                'max_monitored_domains': -1,  # Unlimited
                'max_alert_rules': -1,  # Unlimited
                'retention_days': -1,  # Unlimited
                'has_api_access': True,
                'has_webhooks': True,
                'has_priority_support': True,
                'has_custom_integrations': True,
                'has_advanced_analytics': True,
                'status': 'active',
            },
        ]

        for plan_data in plans:
            plan, created = Subscription.objects.update_or_create(
                plan_type=plan_data['plan_type'],
                billing_cycle=plan_data['billing_cycle'],
                defaults={
                    **plan_data,
                    'current_period_end': timezone.now() + timedelta(days=30),
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {plan.plan_type} plan')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Updated {plan.plan_type} plan')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created/updated all subscription plans')
        )

