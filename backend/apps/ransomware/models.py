from django.db import models
from django.utils import timezone
import uuid


class RansomwareGroup(models.Model):
    """Ransomware threat actor groups"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    aliases = models.JSONField(default=list)  # Alternative names
    description = models.TextField(blank=True, null=True)
    first_seen = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
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
        db_table = 'ransomware_groups'
        ordering = ['-threat_level', 'name']
    
    def __str__(self):
        return self.name


class RansomwareIncident(models.Model):
    """Ransomware attack incidents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='ransomware_incidents',
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        RansomwareGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents'
    )
    victim_name = models.CharField(max_length=255)
    victim_industry = models.CharField(max_length=100, blank=True, null=True)
    victim_country = models.CharField(max_length=100, blank=True, null=True)
    announced_date = models.DateField()
    leak_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('announced', 'Announced'),
            ('leaked', 'Leaked'),
            ('resolved', 'Resolved'),
        ],
        default='announced'
    )
    description = models.TextField(blank=True, null=True)
    data_types = models.JSONField(default=list)  # Types of data leaked
    estimated_impact = models.CharField(max_length=50, blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ransomware_incidents'
        indexes = [
            models.Index(fields=['announced_date']),
            models.Index(fields=['group', 'announced_date']),
            models.Index(fields=['victim_industry']),
        ]
        ordering = ['-announced_date']
    
    def __str__(self):
        return f"{self.victim_name} - {self.group.name if self.group else 'Unknown'}"


class RansomwareMonitor(models.Model):
    """Organization-specific ransomware monitoring configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='ransomware_monitors'
    )
    name = models.CharField(max_length=255)
    keywords = models.JSONField(default=list)  # Keywords to monitor
    industries = models.JSONField(default=list)  # Industries to monitor
    countries = models.JSONField(default=list)  # Countries to monitor
    groups = models.ManyToManyField(RansomwareGroup, blank=True)
    is_active = models.BooleanField(default=True)
    alert_on_new_incident = models.BooleanField(default=True)
    alert_on_leak = models.BooleanField(default=True)
    webhook_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ransomware_monitors'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"
