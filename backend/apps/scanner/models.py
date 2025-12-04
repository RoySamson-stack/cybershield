from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class ScanTarget(models.Model):
    """Targets for security scanning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='scan_targets'
    )
    name = models.CharField(max_length=255)
    target_type = models.CharField(
        max_length=20,
        choices=[
            ('domain', 'Domain'),
            ('ip', 'IP Address'),
            ('url', 'URL'),
            ('subdomain', 'Subdomain'),
        ]
    )
    target_value = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    scan_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('manual', 'Manual'),
        ],
        default='weekly'
    )
    last_scan_at = models.DateTimeField(null=True, blank=True)
    next_scan_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scan_targets'
        unique_together = ['organization', 'target_value']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.target_value})"


class SecurityScan(models.Model):
    """Security scan results"""
    SCAN_TYPES = [
        ('vulnerability', 'Vulnerability Scan'),
        ('ssl', 'SSL/TLS Scan'),
        ('dns', 'DNS Scan'),
        ('port', 'Port Scan'),
        ('web', 'Web Application Scan'),
        ('full', 'Full Scan'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='security_scans'
    )
    target = models.ForeignKey(
        ScanTarget,
        on_delete=models.CASCADE,
        related_name='scans'
    )
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Results
    vulnerabilities_found = models.IntegerField(default=0)
    vulnerabilities_critical = models.IntegerField(default=0)
    vulnerabilities_high = models.IntegerField(default=0)
    vulnerabilities_medium = models.IntegerField(default=0)
    vulnerabilities_low = models.IntegerField(default=0)
    
    risk_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    results = models.JSONField(default=dict)  # Detailed scan results
    error_message = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_scans'
        indexes = [
            models.Index(fields=['organization', 'status', 'created_at']),
            models.Index(fields=['target', 'created_at']),
            models.Index(fields=['scan_type', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.target.name} - {self.scan_type} ({self.status})"


class Vulnerability(models.Model):
    """Vulnerability findings"""
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Informational'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan = models.ForeignKey(
        SecurityScan,
        on_delete=models.CASCADE,
        related_name='vulnerabilities'
    )
    cve_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    cvss_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    affected_component = models.CharField(max_length=255, blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    references = models.JSONField(default=list)
    is_false_positive = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vulnerabilities'
        indexes = [
            models.Index(fields=['scan', 'severity']),
            models.Index(fields=['cve_id']),
            models.Index(fields=['is_resolved', 'severity']),
        ]
        ordering = ['-severity', '-cvss_score', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.severity})"
