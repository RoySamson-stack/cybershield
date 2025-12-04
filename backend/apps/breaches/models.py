from django.db import models
from django.utils import timezone
import uuid


class DataBreach(models.Model):
    """Data breach incidents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='data_breaches',
        null=True,
        blank=True
    )
    breach_name = models.CharField(max_length=255)
    affected_organization = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    breach_date = models.DateField(null=True, blank=True)
    discovered_date = models.DateField(null=True, blank=True)
    disclosed_date = models.DateField(null=True, blank=True)
    records_affected = models.BigIntegerField(null=True, blank=True)
    data_types = models.JSONField(default=list)  # e.g., ['email', 'password', 'credit_card']
    breach_type = models.CharField(
        max_length=50,
        choices=[
            ('hack', 'Hack'),
            ('insider', 'Insider Threat'),
            ('accidental', 'Accidental Exposure'),
            ('physical', 'Physical Theft'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
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
    description = models.TextField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_breaches'
        indexes = [
            models.Index(fields=['breach_date']),
            models.Index(fields=['affected_organization']),
            models.Index(fields=['industry', 'breach_date']),
        ]
        ordering = ['-breach_date', '-created_at']
    
    def __str__(self):
        return f"{self.affected_organization} - {self.breach_name}"


class BreachMonitor(models.Model):
    """Organization-specific breach monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='breach_monitors'
    )
    name = models.CharField(max_length=255)
    keywords = models.JSONField(default=list)
    industries = models.JSONField(default=list)
    countries = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    alert_on_new_breach = models.BooleanField(default=True)
    alert_on_high_severity = models.BooleanField(default=True)
    webhook_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'breach_monitors'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"
