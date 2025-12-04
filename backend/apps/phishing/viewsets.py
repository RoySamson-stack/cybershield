from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PhishingCampaign, PhishingDomain, PhishingMonitor
from .serializers import (
    PhishingCampaignSerializer, PhishingDomainSerializer,
    PhishingMonitorSerializer
)
from apps.core.permissions import IsOrganizationMember


class PhishingCampaignViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for phishing campaigns"""
    serializer_class = PhishingCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PhishingCampaign.objects.all()
        
        # Filter by target brand
        target_brand = self.request.query_params.get('target_brand')
        if target_brand:
            queryset = queryset.filter(target_brand=target_brand)
        
        # Filter by threat level
        threat_level = self.request.query_params.get('threat_level')
        if threat_level:
            queryset = queryset.filter(threat_level=threat_level)
        
        return queryset.order_by('-first_seen', '-threat_level')


class PhishingDomainViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for phishing domains"""
    serializer_class = PhishingDomainSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PhishingDomain.objects.all()
        
        # Filter by campaign
        campaign_id = self.request.query_params.get('campaign')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by target brand
        target_brand = self.request.query_params.get('target_brand')
        if target_brand:
            queryset = queryset.filter(target_brand=target_brand)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-last_seen')


class PhishingMonitorViewSet(viewsets.ModelViewSet):
    """ViewSet for phishing monitors"""
    serializer_class = PhishingMonitorSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return PhishingMonitor.objects.none()
        return PhishingMonitor.objects.filter(organization=organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)

