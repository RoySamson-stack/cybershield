from django.db import models
from django.utils import timezone
import uuid


class GitHubRepository(models.Model):
    """Tracked GitHub repositories for CVE/exploit monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='github_repositories',
        null=True,
        blank=True
    )
    
    # Repository Information
    owner = models.CharField(max_length=255)  # e.g., '0xMarcio'
    repo_name = models.CharField(max_length=255)  # e.g., 'cve'
    full_name = models.CharField(max_length=500, unique=True, db_index=True)  # e.g., '0xMarcio/cve'
    description = models.TextField(blank=True, null=True)
    url = models.URLField()
    default_branch = models.CharField(max_length=100, default='main')
    
    # Monitoring Settings
    is_active = models.BooleanField(default=True)
    monitor_frequency = models.CharField(
        max_length=20,
        choices=[
            ('5min', 'Every 5 minutes'),
            ('15min', 'Every 15 minutes'),
            ('30min', 'Every 30 minutes'),
            ('1hour', 'Every hour'),
            ('6hours', 'Every 6 hours'),
            ('12hours', 'Every 12 hours'),
            ('24hours', 'Every 24 hours'),
        ],
        default='1hour'
    )
    
    # Tracking Data
    last_commit_sha = models.CharField(max_length=40, blank=True, null=True)
    last_commit_date = models.DateTimeField(null=True, blank=True)
    total_commits = models.IntegerField(default=0)
    total_cves_found = models.IntegerField(default=0)
    
    # Status
    last_check_at = models.DateTimeField(null=True, blank=True)
    last_successful_check = models.DateTimeField(null=True, blank=True)
    check_error = models.TextField(blank=True, null=True)
    consecutive_failures = models.IntegerField(default=0)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'github_repositories'
        indexes = [
            models.Index(fields=['full_name']),
            models.Index(fields=['is_active', 'monitor_frequency']),
            models.Index(fields=['last_check_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name}"


class GitHubCVERef(models.Model):
    """CVE references found in GitHub repositories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repository = models.ForeignKey(
        GitHubRepository,
        on_delete=models.CASCADE,
        related_name='cve_refs'
    )
    
    # CVE Information
    cve_id = models.CharField(max_length=50, db_index=True)  # e.g., CVE-2024-1234
    file_path = models.CharField(max_length=1000)  # Path in repository
    commit_sha = models.CharField(max_length=40)
    commit_date = models.DateTimeField()
    commit_message = models.TextField(blank=True, null=True)
    
    # Repository Info
    branch = models.CharField(max_length=100, default='main')
    url = models.URLField()  # Direct link to file/commit
    
    # Status
    is_new = models.BooleanField(default=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'github_cve_refs'
        indexes = [
            models.Index(fields=['repository', 'cve_id']),
            models.Index(fields=['cve_id', 'is_new']),
            models.Index(fields=['commit_date']),
        ]
        unique_together = ['repository', 'cve_id', 'commit_sha']
        ordering = ['-commit_date']
    
    def __str__(self):
        return f"{self.cve_id} in {self.repository.full_name}"


class RansomwareSite(models.Model):
    """Onion sites scraped from ransomware.live"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='ransomware_sites',
        null=True,
        blank=True
    )
    
    # Site Information
    group_name = models.CharField(max_length=255, db_index=True)  # e.g., 'LockBit'
    onion_address = models.CharField(max_length=500, unique=True, db_index=True)  # .onion address
    clearnet_url = models.URLField(blank=True, null=True)  # If available
    site_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('seized', 'Seized'),
            ('unknown', 'Unknown'),
        ],
        default='active'
    )
    
    # Scraping Data
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_successful_check = models.DateTimeField(null=True, blank=True)
    check_count = models.IntegerField(default=0)
    consecutive_failures = models.IntegerField(default=0)
    
    # Content Tracking
    last_post_count = models.IntegerField(default=0)
    current_post_count = models.IntegerField(default=0)
    has_new_posts = models.BooleanField(default=False)
    
    # Source
    source = models.CharField(max_length=100, default='ransomware.live')
    source_url = models.URLField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ransomware_sites'
        indexes = [
            models.Index(fields=['group_name']),
            models.Index(fields=['onion_address']),
            models.Index(fields=['is_active', 'status']),
            models.Index(fields=['last_checked_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.group_name} - {self.onion_address}"


class RansomwarePost(models.Model):
    """Posts/victims found on ransomware sites"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(
        RansomwareSite,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    # Post Information
    post_id = models.CharField(max_length=255, db_index=True)  # Unique ID from site
    title = models.CharField(max_length=500)
    content = models.TextField(blank=True, null=True)
    victim_name = models.CharField(max_length=500, blank=True, null=True)
    
    # Dates
    posted_date = models.DateTimeField(null=True, blank=True)
    discovered_date = models.DateTimeField(auto_now_add=True)
    
    # Status
    is_new = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)
    removed_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ransomware_posts'
        indexes = [
            models.Index(fields=['site', 'posted_date']),
            models.Index(fields=['post_id', 'site']),
            models.Index(fields=['is_new', 'discovered_date']),
        ]
        unique_together = ['site', 'post_id']
        ordering = ['-posted_date', '-discovered_date']
    
    def __str__(self):
        return f"{self.title} - {self.site.group_name}"

