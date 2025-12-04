from rest_framework import serializers
from .models import ScanTarget, SecurityScan, Vulnerability


class ScanTargetSerializer(serializers.ModelSerializer):
    """Serializer for scan targets"""
    last_scan_status = serializers.CharField(source='scans.first.status', read_only=True)
    last_scan_date = serializers.DateTimeField(source='scans.first.completed_at', read_only=True)
    
    class Meta:
        model = ScanTarget
        fields = [
            'id', 'name', 'target_type', 'target_value', 'is_active',
            'scan_frequency', 'last_scan_at', 'next_scan_at',
            'last_scan_status', 'last_scan_date', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_scan_at', 'next_scan_at']


class VulnerabilitySerializer(serializers.ModelSerializer):
    """Serializer for vulnerabilities"""
    
    class Meta:
        model = Vulnerability
        fields = [
            'id', 'cve_id', 'title', 'description', 'severity',
            'cvss_score', 'affected_component', 'recommendation',
            'references', 'is_false_positive', 'is_resolved',
            'resolved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SecurityScanSerializer(serializers.ModelSerializer):
    """Serializer for security scans"""
    target_name = serializers.CharField(source='target.name', read_only=True)
    target_value = serializers.CharField(source='target.target_value', read_only=True)
    vulnerabilities = VulnerabilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = SecurityScan
        fields = [
            'id', 'target', 'target_name', 'target_value', 'scan_type',
            'status', 'started_at', 'completed_at', 'duration_seconds',
            'vulnerabilities_found', 'vulnerabilities_critical',
            'vulnerabilities_high', 'vulnerabilities_medium',
            'vulnerabilities_low', 'risk_score', 'results',
            'error_message', 'vulnerabilities', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'started_at', 'completed_at', 'duration_seconds',
            'vulnerabilities_found', 'vulnerabilities_critical',
            'vulnerabilities_high', 'vulnerabilities_medium',
            'vulnerabilities_low', 'risk_score', 'results',
            'error_message', 'created_at', 'updated_at'
        ]

