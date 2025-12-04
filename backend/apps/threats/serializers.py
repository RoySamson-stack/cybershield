from rest_framework import serializers
from .models import C2Server, OnionSite, OnionDataPost, LeakedCredential, ThreatIntelligence


class C2ServerSerializer(serializers.ModelSerializer):
    """Serializer for C2 servers"""
    
    class Meta:
        model = C2Server
        fields = [
            'id', 'ip_address', 'domain', 'hostname', 'port', 'protocol',
            'c2_family', 'malware_family', 'first_seen', 'last_seen',
            'is_active', 'country', 'asn', 'threat_level', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'first_seen', 'last_seen']


class OnionSiteSerializer(serializers.ModelSerializer):
    """Serializer for onion sites"""
    post_count = serializers.IntegerField(source='data_posts.count', read_only=True)
    
    class Meta:
        model = OnionSite
        fields = [
            'id', 'onion_address', 'title', 'description', 'site_type',
            'is_active', 'first_seen', 'last_checked', 'last_updated',
            'post_count', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'first_seen']


class OnionDataPostSerializer(serializers.ModelSerializer):
    """Serializer for onion data posts"""
    onion_site_address = serializers.CharField(source='onion_site.onion_address', read_only=True)
    
    class Meta:
        model = OnionDataPost
        fields = [
            'id', 'onion_site', 'onion_site_address', 'post_title', 'post_content',
            'posted_date', 'discovered_date', 'data_types', 'affected_organization',
            'record_count', 'is_verified', 'source_url', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'discovered_date']


class LeakedCredentialSerializer(serializers.ModelSerializer):
    """Serializer for leaked credentials"""
    
    class Meta:
        model = LeakedCredential
        fields = [
            'id', 'email', 'username', 'domain', 'breach_source',
            'leak_date', 'discovered_date', 'data_types', 'is_verified',
            'is_exposed', 'source_url', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'discovered_date']
        # Note: password fields excluded for security


class ThreatIntelligenceSerializer(serializers.ModelSerializer):
    """Serializer for threat intelligence"""
    
    class Meta:
        model = ThreatIntelligence
        fields = [
            'id', 'threat_type', 'title', 'description', 'severity',
            'indicators', 'affected_countries', 'affected_industries',
            'first_seen', 'last_seen', 'source', 'source_url', 'is_verified',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

