from django.contrib import admin
from .models import GitHubRepository, GitHubCVERef, RansomwareSite, RansomwarePost


@admin.register(GitHubRepository)
class GitHubRepositoryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'is_active', 'monitor_frequency', 'total_cves_found', 'last_check_at']
    list_filter = ['is_active', 'monitor_frequency', 'created_at']
    search_fields = ['full_name', 'owner', 'repo_name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(GitHubCVERef)
class GitHubCVERefAdmin(admin.ModelAdmin):
    list_display = ['cve_id', 'repository', 'commit_date', 'is_new', 'is_processed']
    list_filter = ['is_new', 'is_processed', 'commit_date']
    search_fields = ['cve_id', 'repository__full_name', 'file_path']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(RansomwareSite)
class RansomwareSiteAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'onion_address', 'status', 'is_active', 'last_checked_at']
    list_filter = ['status', 'is_active', 'source', 'created_at']
    search_fields = ['group_name', 'onion_address', 'site_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(RansomwarePost)
class RansomwarePostAdmin(admin.ModelAdmin):
    list_display = ['title', 'site', 'posted_date', 'is_new', 'is_removed']
    list_filter = ['is_new', 'is_removed', 'posted_date', 'discovered_date']
    search_fields = ['title', 'victim_name', 'site__group_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'discovered_date']

