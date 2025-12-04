from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import DataBreach, BreachMonitor
from .serializers import DataBreachSerializer, BreachMonitorSerializer
from apps.core.permissions import IsOrganizationMember


class DataBreachViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for data breaches"""
    serializer_class = DataBreachSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DataBreach.objects.all()
        
        # Filter by industry
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(industry=industry)
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country=country)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by breach type
        breach_type = self.request.query_params.get('breach_type')
        if breach_type:
            queryset = queryset.filter(breach_type=breach_type)
        
        return queryset.order_by('-breach_date', '-created_at')


class BreachMonitorViewSet(viewsets.ModelViewSet):
    """ViewSet for breach monitors"""
    serializer_class = BreachMonitorSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return BreachMonitor.objects.none()
        return BreachMonitor.objects.filter(organization=organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)

