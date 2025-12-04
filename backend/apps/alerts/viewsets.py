from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import AlertRule, Alert
from .serializers import AlertRuleSerializer, AlertSerializer
from apps.core.permissions import IsOrganizationMember


class AlertRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for alert rules"""
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return AlertRule.objects.none()
        return AlertRule.objects.filter(organization=organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet for alerts"""
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return Alert.objects.none()
        
        queryset = Alert.objects.filter(organization=organization)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by alert type
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

