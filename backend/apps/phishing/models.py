from django.db import models
from django.utils import timezone
import uuid


class PhishingCampaign(models.Model):
    """Phishing campaign tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='phishing_campaigns',
        null=True,
        blank=True
    )
    campaign_name = models.CharField(max_length=255)
    target_brand = models.CharField(max_length=255, blank=True, null=True)
    first_seen = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
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
    description = models.TextField(blank=True, null=True)
    source_urls = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'phishing_campaigns'
        ordering = ['-first_seen', '-threat_level']
    
    def __str__(self):
        return self.campaign_name


class PhishingDomain(models.Model):
    """Phishing domain monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='phishing_domains',
        null=True,
        blank=True
    )
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    campaign = models.ForeignKey(
        PhishingCampaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='domains'
    )
    target_brand = models.CharField(max_length=255, blank=True, null=True)
    registrar = models.CharField(max_length=255, blank=True, null=True)
    registration_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'phishing_domains'
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_active', 'last_seen']),
        ]
        ordering = ['-last_seen']
    
    def __str__(self):
        return self.domain


class PhishingMonitor(models.Model):
    """Organization-specific phishing monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='phishing_monitors'
    )
    name = models.CharField(max_length=255)
    keywords = models.JSONField(default=list)
    target_brands = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    alert_on_new_domain = models.BooleanField(default=True)
    alert_on_new_campaign = models.BooleanField(default=True)
    webhook_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'phishing_monitors'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"
