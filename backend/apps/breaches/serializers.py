from rest_framework import serializers
from .models import DataBreach, BreachMonitor


class DataBreachSerializer(serializers.ModelSerializer):
    """Serializer for data breaches"""
    
    class Meta:
        model = DataBreach
        fields = [
            'id', 'breach_name', 'affected_organization', 'industry',
            'country', 'breach_date', 'discovered_date', 'disclosed_date',
            'records_affected', 'data_types', 'breach_type', 'severity',
            'description', 'source_url', 'is_verified', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BreachMonitorSerializer(serializers.ModelSerializer):
    """Serializer for breach monitors"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = BreachMonitor
        fields = [
            'id', 'organization', 'organization_name', 'name', 'keywords',
            'industries', 'countries', 'is_active', 'alert_on_new_breach',
            'alert_on_high_severity', 'webhook_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

