from django.db import models
from django.utils import timezone
import uuid


class AlertRule(models.Model):
    """Alert rules for notifications"""
    ALERT_TYPES = [
        ('ransomware_incident', 'Ransomware Incident'),
        ('data_breach', 'Data Breach'),
        ('vulnerability', 'Vulnerability Found'),
        ('phishing_domain', 'Phishing Domain Detected'),
        ('scan_completed', 'Scan Completed'),
        ('scan_failed', 'Scan Failed'),
        ('usage_limit', 'Usage Limit Reached'),
    ]
    
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('sms', 'SMS'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='alert_rules'
    )
    name = models.CharField(max_length=255)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    channel_config = models.JSONField(default=dict)  # Channel-specific config
    conditions = models.JSONField(default=dict)  # Alert conditions
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_rules'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class Alert(models.Model):
    """Alert instances"""
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('acknowledged', 'Acknowledged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    title = models.CharField(max_length=500)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    resource_type = models.CharField(max_length=50, blank=True, null=True)
    resource_id = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict)
    sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alerts'
        indexes = [
            models.Index(fields=['organization', 'status', 'created_at']),
            models.Index(fields=['alert_type', 'severity']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.severity})"
