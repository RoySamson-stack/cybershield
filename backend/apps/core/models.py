from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class User(AbstractUser):
    """Extended user model with enterprise features"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Admin'),
            ('member', 'Member'),
            ('viewer', 'Viewer'),
        ],
        default='member'
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']


class Organization(models.Model):
    """Multi-tenant organization model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    domain = models.CharField(max_length=255, blank=True, null=True)
    subscription = models.OneToOneField(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organization'
    )
    is_active = models.BooleanField(default=True)
    max_users = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    max_api_keys = models.IntegerField(default=3, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Subscription plans for monetization"""
    PLAN_TYPES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='free')
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLES, default='monthly')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Feature limits
    max_scans_per_month = models.IntegerField(default=100)
    max_api_requests_per_month = models.IntegerField(default=10000)
    max_monitored_domains = models.IntegerField(default=5)
    max_alert_rules = models.IntegerField(default=10)
    retention_days = models.IntegerField(default=30)
    
    # Features
    has_api_access = models.BooleanField(default=False)
    has_webhooks = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    has_custom_integrations = models.BooleanField(default=False)
    has_advanced_analytics = models.BooleanField(default=False)
    has_threat_intelligence = models.BooleanField(default=False)  # Pro-tier threat intelligence
    has_malware_analysis = models.BooleanField(default=False)  # Malware analysis features
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
            ('trial', 'Trial'),
        ],
        default='trial'
    )
    
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.plan_type} - {self.billing_cycle}"


class APIKey(models.Model):
    """API keys for programmatic access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=64, unique=True, db_index=True)
    key_prefix = models.CharField(max_length=8)  # First 8 chars for identification
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    rate_limit_per_hour = models.IntegerField(default=1000)
    scopes = models.JSONField(default=list)  # List of allowed endpoints
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_api_keys'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class UsageMetrics(models.Model):
    """Track API usage for billing and rate limiting"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='usage_metrics'
    )
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usage_metrics'
    )
    metric_type = models.CharField(
        max_length=50,
        choices=[
            ('api_request', 'API Request'),
            ('scan', 'Security Scan'),
            ('webhook', 'Webhook'),
            ('data_export', 'Data Export'),
        ]
    )
    count = models.IntegerField(default=1)
    metadata = models.JSONField(default=dict)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'usage_metrics'
        unique_together = ['organization', 'metric_type', 'date']
        indexes = [
            models.Index(fields=['organization', 'date']),
            models.Index(fields=['api_key', 'date']),
        ]
        ordering = ['-date', '-created_at']


class AuditLog(models.Model):
    """Comprehensive audit logging for compliance"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('api_call', 'API Call'),
        ('config_change', 'Configuration Change'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=50)  # e.g., 'user', 'scan', 'api_key'
    resource_id = models.CharField(max_length=255)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
        ]
        ordering = ['-created_at']


class HealthCheck(models.Model):
    """System health check records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('healthy', 'Healthy'),
            ('degraded', 'Degraded'),
            ('unhealthy', 'Unhealthy'),
        ]
    )
    response_time_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    checked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'health_checks'
        ordering = ['-checked_at']


class C2Server(models.Model):
    """Command and Control server tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='c2_servers',
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    domain = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    port = models.IntegerField(null=True, blank=True)
    protocol = models.CharField(max_length=20, default='http')  # http, https, tcp, udp
    c2_family = models.CharField(max_length=100, blank=True, null=True)  # Cobalt Strike, Metasploit, etc.
    malware_family = models.CharField(max_length=100, blank=True, null=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    asn = models.CharField(max_length=50, blank=True, null=True)
    threat_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'c2_servers'
        indexes = [
            models.Index(fields=['domain', 'is_active']),
            models.Index(fields=['ip_address', 'is_active']),
            models.Index(fields=['c2_family', 'threat_level']),
        ]
        ordering = ['-last_seen', '-threat_level']
    
    def __str__(self):
        return f"{self.domain or self.ip_address} ({self.c2_family or 'Unknown'})"


class OnionSite(models.Model):
    """Dark web / Onion site monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='onion_sites',
        null=True,
        blank=True
    )
    onion_address = models.CharField(max_length=255, unique=True, db_index=True)  # .onion address
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    site_type = models.CharField(
        max_length=50,
        choices=[
            ('marketplace', 'Marketplace'),
            ('forum', 'Forum'),
            ('leak_site', 'Leak Site'),
            ('ransomware', 'Ransomware Group'),
            ('other', 'Other'),
        ],
        default='other'
    )
    is_active = models.BooleanField(default=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'onion_sites'
        indexes = [
            models.Index(fields=['onion_address', 'is_active']),
            models.Index(fields=['site_type', 'is_active']),
        ]
        ordering = ['-last_checked', '-first_seen']
    
    def __str__(self):
        return f"{self.onion_address} ({self.site_type})"


class OnionDataPost(models.Model):
    """Track when data is posted on onion sites"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='onion_data_posts',
        null=True,
        blank=True
    )
    onion_site = models.ForeignKey(
        OnionSite,
        on_delete=models.CASCADE,
        related_name='data_posts'
    )
    post_title = models.CharField(max_length=500)
    post_content = models.TextField(blank=True, null=True)
    posted_date = models.DateTimeField(null=True, blank=True)
    discovered_date = models.DateTimeField(auto_now_add=True)
    data_types = models.JSONField(default=list)  # email, password, credit_card, etc.
    affected_organization = models.CharField(max_length=255, blank=True, null=True)
    record_count = models.BigIntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    source_url = models.URLField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'onion_data_posts'
        indexes = [
            models.Index(fields=['onion_site', 'posted_date']),
            models.Index(fields=['affected_organization', 'posted_date']),
            models.Index(fields=['discovered_date']),
        ]
        ordering = ['-posted_date', '-discovered_date']
    
    def __str__(self):
        return f"{self.post_title} - {self.onion_site.onion_address}"


class LeakedCredential(models.Model):
    """Store for leaked credentials found online"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='leaked_credentials',
        null=True,
        blank=True
    )
    email = models.EmailField(db_index=True)
    username = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    password_hash = models.CharField(max_length=255, blank=True, null=True)  # Hashed password
    password_plain = models.CharField(max_length=255, blank=True, null=True)  # Plain text (encrypted at rest)
    domain = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    breach_source = models.CharField(max_length=255, blank=True, null=True)  # Which breach this came from
    leak_date = models.DateField(null=True, blank=True)
    discovered_date = models.DateTimeField(auto_now_add=True)
    data_types = models.JSONField(default=list)  # Additional data types
    is_verified = models.BooleanField(default=False)
    is_exposed = models.BooleanField(default=False)  # If this credential is publicly exposed
    source_url = models.URLField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaked_credentials'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['domain']),
            models.Index(fields=['breach_source', 'leak_date']),
            models.Index(fields=['is_exposed', 'discovered_date']),
        ]
        ordering = ['-discovered_date', '-leak_date']
    
    def __str__(self):
        return f"{self.email} ({self.breach_source or 'Unknown'})"


class ThreatIntelligence(models.Model):
    """Comprehensive threat intelligence tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='threat_intelligence',
        null=True,
        blank=True
    )
    threat_type = models.CharField(
        max_length=50,
        choices=[
            ('ransomware', 'Ransomware'),
            ('data_breach', 'Data Breach'),
            ('phishing', 'Phishing'),
            ('c2', 'C2 Server'),
            ('malware', 'Malware'),
            ('apt', 'APT'),
            ('vulnerability', 'Vulnerability'),
            ('other', 'Other'),
        ]
    )
    title = models.CharField(max_length=500)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    indicators = models.JSONField(default=dict)  # IPs, domains, hashes, etc.
    affected_countries = models.JSONField(default=list)
    affected_industries = models.JSONField(default=list)
    first_seen = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'threat_intelligence'
        indexes = [
            models.Index(fields=['threat_type', 'severity']),
            models.Index(fields=['severity', 'first_seen']),
            models.Index(fields=['is_verified', 'created_at']),
        ]
        ordering = ['-severity', '-first_seen', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.threat_type})"
