from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import RansomwareGroup, RansomwareIncident, RansomwareMonitor
from .serializers import (
    RansomwareGroupSerializer, RansomwareIncidentSerializer,
    RansomwareMonitorSerializer
)
from apps.core.permissions import IsOrganizationMember


class RansomwareGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ransomware groups"""
    serializer_class = RansomwareGroupSerializer
    permission_classes = [IsAuthenticated]
    queryset = RansomwareGroup.objects.all()
    
    def get_queryset(self):
        queryset = RansomwareGroup.objects.all()
        
        # Filter by threat level
        threat_level = self.request.query_params.get('threat_level')
        if threat_level:
            queryset = queryset.filter(threat_level=threat_level)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-threat_level', 'name')


class RansomwareIncidentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ransomware incidents"""
    serializer_class = RansomwareIncidentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = RansomwareIncident.objects.all()
        
        # Filter by group
        group_id = self.request.query_params.get('group')
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        
        # Filter by industry
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(victim_industry=industry)
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(victim_country=country)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-announced_date')


class RansomwareMonitorViewSet(viewsets.ModelViewSet):
    """ViewSet for ransomware monitors"""
    serializer_class = RansomwareMonitorSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return RansomwareMonitor.objects.none()
        return RansomwareMonitor.objects.filter(organization=organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)

