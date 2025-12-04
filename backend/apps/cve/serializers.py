from rest_framework import serializers
from .models import CVE, CVEComment


class CVESerializer(serializers.ModelSerializer):
    """Serializer for CVE"""
    shared_by_username = serializers.CharField(source='shared_by.username', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    
    class Meta:
        model = CVE
        fields = [
            'id', 'cve_id', 'title', 'description', 'severity',
            'cvss_v3_score', 'cvss_v2_score', 'cvss_v3_vector',
            'affected_products', 'affected_versions', 'vendor',
            'has_exploit', 'exploit_available', 'poc_available',
            'poc_url', 'github_repo', 'exploit_maturity',
            'cwe_id', 'published_date', 'modified_date', 'discovered_date',
            'status', 'is_verified', 'is_publicly_exploited',
            'references', 'advisory_url', 'mitre_url', 'nvd_url',
            'shared_by_username', 'upvotes', 'views', 'comment_count',
            'tags', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'views']


class CVECommentSerializer(serializers.ModelSerializer):
    """Serializer for CVE comments"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CVEComment
        fields = [
            'id', 'cve', 'username', 'content',
            'is_verified_expert', 'upvotes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'upvotes']

