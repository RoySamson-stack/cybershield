from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Organization, Subscription, APIKey,
    UsageMetrics, AuditLog, HealthCheck
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'organization', 'role', 'is_verified', 'is_active']
    list_filter = ['role', 'is_verified', 'is_active', 'organization']
    search_fields = ['email', 'username']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Organization', {'fields': ('organization', 'role')}),
        ('Additional Info', {'fields': ('phone', 'is_verified', 'last_login_ip')}),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'subscription', 'is_active', 'max_users', 'created_at']
    list_filter = ['is_active', 'subscription__plan_type']
    search_fields = ['name', 'slug', 'domain']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'plan_type', 'billing_cycle', 'price', 'status',
        'current_period_end', 'cancel_at_period_end'
    ]
    list_filter = ['plan_type', 'billing_cycle', 'status']
    search_fields = ['stripe_subscription_id', 'stripe_customer_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Plan Details', {
            'fields': ('plan_type', 'billing_cycle', 'price', 'status')
        }),
        ('Limits', {
            'fields': (
                'max_scans_per_month', 'max_api_requests_per_month',
                'max_monitored_domains', 'max_alert_rules', 'retention_days'
            )
        }),
        ('Features', {
            'fields': (
                'has_api_access', 'has_webhooks', 'has_priority_support',
                'has_custom_integrations', 'has_advanced_analytics'
            )
        }),
        ('Billing', {
            'fields': (
                'current_period_start', 'current_period_end',
                'cancel_at_period_end', 'stripe_subscription_id', 'stripe_customer_id'
            )
        }),
    )


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'key_prefix', 'is_active', 'last_used_at', 'rate_limit_per_hour']
    list_filter = ['is_active', 'organization']
    search_fields = ['name', 'key_prefix', 'organization__name']
    readonly_fields = ['id', 'key', 'key_prefix', 'created_at', 'updated_at', 'last_used_at', 'last_used_ip']
    exclude = ['key']  # Don't show full key in admin


@admin.register(UsageMetrics)
class UsageMetricsAdmin(admin.ModelAdmin):
    list_display = ['organization', 'api_key', 'metric_type', 'count', 'date', 'created_at']
    list_filter = ['metric_type', 'date', 'organization']
    search_fields = ['organization__name']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'date'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'resource_type', 'organization', 'user', 'ip_address', 'created_at']
    list_filter = ['action_type', 'resource_type', 'created_at']
    search_fields = ['description', 'organization__name', 'user__email']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'status', 'response_time_ms', 'checked_at']
    list_filter = ['status', 'service_name', 'checked_at']
    readonly_fields = ['id', 'checked_at']
    date_hierarchy = 'checked_at'
