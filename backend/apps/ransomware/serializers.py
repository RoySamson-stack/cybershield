from rest_framework import serializers
from .models import RansomwareGroup, RansomwareIncident, RansomwareMonitor


class RansomwareGroupSerializer(serializers.ModelSerializer):
    """Serializer for ransomware groups"""
    incident_count = serializers.IntegerField(source='incidents.count', read_only=True)
    
    class Meta:
        model = RansomwareGroup
        fields = [
            'id', 'name', 'aliases', 'description', 'first_seen',
            'is_active', 'threat_level', 'incident_count', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RansomwareIncidentSerializer(serializers.ModelSerializer):
    """Serializer for ransomware incidents"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = RansomwareIncident
        fields = [
            'id', 'group', 'group_name', 'victim_name', 'victim_industry',
            'victim_country', 'announced_date', 'leak_date', 'status',
            'description', 'data_types', 'estimated_impact', 'source_url',
            'is_verified', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RansomwareMonitorSerializer(serializers.ModelSerializer):
    """Serializer for ransomware monitors"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    groups_list = serializers.SerializerMethodField()
    
    class Meta:
        model = RansomwareMonitor
        fields = [
            'id', 'organization', 'organization_name', 'name', 'keywords',
            'industries', 'countries', 'groups', 'groups_list', 'is_active',
            'alert_on_new_incident', 'alert_on_leak', 'webhook_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_groups_list(self, obj):
        return [group.name for group in obj.groups.all()]

