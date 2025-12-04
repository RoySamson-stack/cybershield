from rest_framework import serializers
from .models import GitHubRepository, GitHubCVERef, RansomwareSite, RansomwarePost


class GitHubRepositorySerializer(serializers.ModelSerializer):
    """Serializer for GitHub repositories"""
    
    class Meta:
        model = GitHubRepository
        fields = [
            'id', 'owner', 'repo_name', 'full_name', 'description', 'url',
            'default_branch', 'is_active', 'monitor_frequency',
            'last_commit_sha', 'last_commit_date', 'total_commits',
            'total_cves_found', 'last_check_at', 'last_successful_check',
            'check_error', 'consecutive_failures', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_commit_sha',
            'last_commit_date', 'total_commits', 'total_cves_found',
            'last_check_at', 'last_successful_check', 'check_error',
            'consecutive_failures'
        ]


class GitHubCVERefSerializer(serializers.ModelSerializer):
    """Serializer for CVE references from GitHub"""
    repository_name = serializers.CharField(source='repository.full_name', read_only=True)
    
    class Meta:
        model = GitHubCVERef
        fields = [
            'id', 'repository', 'repository_name', 'cve_id', 'file_path',
            'commit_sha', 'commit_date', 'commit_message', 'branch', 'url',
            'is_new', 'is_processed', 'processed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RansomwareSiteSerializer(serializers.ModelSerializer):
    """Serializer for ransomware sites"""
    post_count = serializers.IntegerField(source='posts.count', read_only=True)
    new_post_count = serializers.IntegerField(
        source='posts.filter(is_new=True).count',
        read_only=True
    )
    
    class Meta:
        model = RansomwareSite
        fields = [
            'id', 'group_name', 'onion_address', 'clearnet_url', 'site_name',
            'is_active', 'status', 'last_checked_at', 'last_successful_check',
            'check_count', 'consecutive_failures', 'last_post_count',
            'current_post_count', 'has_new_posts', 'source', 'source_url',
            'post_count', 'new_post_count', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_checked_at',
            'last_successful_check', 'check_count', 'consecutive_failures',
            'post_count', 'new_post_count'
        ]


class RansomwarePostSerializer(serializers.ModelSerializer):
    """Serializer for ransomware posts"""
    group_name = serializers.CharField(source='site.group_name', read_only=True)
    onion_address = serializers.CharField(source='site.onion_address', read_only=True)
    
    class Meta:
        model = RansomwarePost
        fields = [
            'id', 'site', 'group_name', 'onion_address', 'post_id', 'title',
            'content', 'victim_name', 'posted_date', 'discovered_date',
            'is_new', 'is_removed', 'removed_date', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'discovered_date']

