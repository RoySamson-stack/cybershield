from rest_framework import serializers
from .models import AlertRule, Alert


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for alert rules"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'organization', 'organization_name', 'name', 'alert_type',
            'channel_type', 'channel_config', 'conditions', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for alerts"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    acknowledged_by_email = serializers.CharField(source='acknowledged_by.email', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'organization', 'organization_name', 'rule', 'rule_name',
            'alert_type', 'severity', 'title', 'message', 'status',
            'resource_type', 'resource_id', 'metadata', 'sent_at',
            'acknowledged_at', 'acknowledged_by', 'acknowledged_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sent_at', 'acknowledged_at', 'acknowledged_by',
            'created_at', 'updated_at'
        ]

