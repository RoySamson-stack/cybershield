from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class CVE(models.Model):
    """Common Vulnerabilities and Exposures tracking"""
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Informational'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('analyzing', 'Analyzing'),
        ('exploited', 'Exploited'),
        ('patched', 'Patched'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='cves',
        null=True,
        blank=True
    )
    
    # CVE Information
    cve_id = models.CharField(max_length=50, unique=True, db_index=True)  # e.g., CVE-2024-1234
    title = models.CharField(max_length=500)
    description = models.TextField()
    
    # Severity and Scoring
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    cvss_v3_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    cvss_v2_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    cvss_v3_vector = models.CharField(max_length=200, blank=True, null=True)
    
    # Affected Products
    affected_products = models.JSONField(default=list)  # List of affected software/products
    affected_versions = models.JSONField(default=list)  # Version ranges
    vendor = models.CharField(max_length=255, blank=True, null=True)
    
    # Exploit Information
    has_exploit = models.BooleanField(default=False)
    exploit_available = models.BooleanField(default=False)
    poc_available = models.BooleanField(default=False)
    poc_url = models.URLField(blank=True, null=True)
    github_repo = models.URLField(blank=True, null=True)
    exploit_maturity = models.CharField(
        max_length=20,
        choices=[
            ('unproven', 'Unproven'),
            ('proof_of_concept', 'Proof of Concept'),
            ('functional', 'Functional'),
            ('high', 'High'),
            ('not_defined', 'Not Defined'),
        ],
        default='not_defined'
    )
    
    # Additional Information
    cwe_id = models.CharField(max_length=50, blank=True, null=True)  # Common Weakness Enumeration
    published_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    discovered_date = models.DateTimeField(null=True, blank=True)
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    is_verified = models.BooleanField(default=False)
    is_publicly_exploited = models.BooleanField(default=False)
    
    # References and Links
    references = models.JSONField(default=list)  # List of reference URLs
    advisory_url = models.URLField(blank=True, null=True)
    mitre_url = models.URLField(blank=True, null=True)
    nvd_url = models.URLField(blank=True, null=True)
    
    # Community Sharing
    shared_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shared_cves'
    )
    upvotes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    
    # Metadata
    tags = models.JSONField(default=list)  # e.g., ['rce', 'sql-injection', 'linux']
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cves'
        indexes = [
            models.Index(fields=['cve_id']),
            models.Index(fields=['severity', 'cvss_v3_score']),
            models.Index(fields=['has_exploit', 'exploit_available']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['published_date']),
            models.Index(fields=['vendor']),
        ]
        ordering = ['-published_date', '-cvss_v3_score', '-created_at']
    
    def __str__(self):
        return f"{self.cve_id} - {self.title}"


class CVEComment(models.Model):
    """Comments on CVEs shared by community"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cve = models.ForeignKey(
        CVE,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='cve_comments'
    )
    content = models.TextField()
    is_verified_expert = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cve_comments'
        ordering = ['-upvotes', '-created_at']
    
    def __str__(self):
        return f"Comment on {self.cve.cve_id} by {self.user.username}"

