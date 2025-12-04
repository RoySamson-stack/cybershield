from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Organization, Subscription, APIKey, UsageMetrics, AuditLog


class UserSerializer(serializers.ModelSerializer):
    """User serializer for API responses"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'organization', 'organization_name', 'role', 'is_verified',
            'phone', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer"""
    member_count = serializers.IntegerField(source='members.count', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan_type', read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'domain', 'subscription',
            'subscription_plan', 'is_active', 'max_users', 'max_api_keys',
            'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating organizations"""
    
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'domain']
    
    def create(self, validated_data):
        organization = Organization.objects.create(**validated_data)
        # Create a free subscription for new organizations
        from .models import Subscription
        from django.utils import timezone
        from datetime import timedelta
        
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
            current_period_end=timezone.now() + timedelta(days=30)
        )
        organization.subscription = subscription
        organization.save()
        return organization


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer"""
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan_type', 'billing_cycle', 'price', 'status',
            'max_scans_per_month', 'max_api_requests_per_month',
            'max_monitored_domains', 'max_alert_rules', 'retention_days',
            'has_api_access', 'has_webhooks', 'has_priority_support',
            'has_custom_integrations', 'has_advanced_analytics',
            'current_period_start', 'current_period_end',
            'cancel_at_period_end', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class APIKeySerializer(serializers.ModelSerializer):
    """API Key serializer (without exposing full key)"""
    key_display = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key_display', 'key_prefix', 'is_active',
            'last_used_at', 'last_used_ip', 'expires_at',
            'rate_limit_per_hour', 'scopes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'key_prefix', 'last_used_at', 'last_used_ip', 'created_at', 'updated_at']
    
    def get_key_display(self, obj):
        """Show only prefix for security"""
        if self.context.get('show_full_key') and hasattr(obj, 'key'):
            return obj.key
        return f"{obj.key_prefix}..."


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API keys"""
    key = serializers.CharField(read_only=True)  # Will be generated
    
    class Meta:
        model = APIKey
        fields = ['name', 'expires_at', 'rate_limit_per_hour', 'scopes']
    
    def create(self, validated_data):
        organization = self.context['request'].organization
        user = self.context['request'].user
        
        # Check API key limit
        current_count = APIKey.objects.filter(organization=organization, is_active=True).count()
        if current_count >= organization.max_api_keys:
            raise serializers.ValidationError(
                f"Maximum API keys limit ({organization.max_api_keys}) reached for your plan"
            )
        
        # Generate API key
        import secrets
        key = secrets.token_urlsafe(32)
        key_prefix = key[:8]
        
        api_key = APIKey.objects.create(
            organization=organization,
            created_by=user,
            key=key,
            key_prefix=key_prefix,
            **validated_data
        )
        
        # Store full key temporarily for response
        api_key.key = key
        return api_key


class UsageMetricsSerializer(serializers.ModelSerializer):
    """Usage metrics serializer"""
    
    class Meta:
        model = UsageMetrics
        fields = [
            'id', 'metric_type', 'count', 'metadata', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'organization', 'organization_name', 'user', 'user_email',
            'action_type', 'resource_type', 'resource_id', 'description',
            'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

