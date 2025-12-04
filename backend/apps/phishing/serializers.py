from rest_framework import serializers
from .models import PhishingCampaign, PhishingDomain, PhishingMonitor


class PhishingCampaignSerializer(serializers.ModelSerializer):
    """Serializer for phishing campaigns"""
    domain_count = serializers.IntegerField(source='domains.count', read_only=True)
    
    class Meta:
        model = PhishingCampaign
        fields = [
            'id', 'campaign_name', 'target_brand', 'first_seen', 'last_seen',
            'threat_level', 'description', 'source_urls', 'domain_count',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PhishingDomainSerializer(serializers.ModelSerializer):
    """Serializer for phishing domains"""
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    
    class Meta:
        model = PhishingDomain
        fields = [
            'id', 'domain', 'campaign', 'campaign_name', 'target_brand',
            'registrar', 'registration_date', 'is_active', 'first_seen',
            'last_seen', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PhishingMonitorSerializer(serializers.ModelSerializer):
    """Serializer for phishing monitors"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = PhishingMonitor
        fields = [
            'id', 'organization', 'organization_name', 'name', 'keywords',
            'target_brands', 'is_active', 'alert_on_new_domain',
            'alert_on_new_campaign', 'webhook_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

