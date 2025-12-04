from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ScanTarget, SecurityScan, Vulnerability
from .serializers import ScanTargetSerializer, SecurityScanSerializer, VulnerabilitySerializer
from .services import ScannerService
from apps.core.permissions import IsOrganizationMember, IsWithinUsageLimit


class ScanTargetViewSet(viewsets.ModelViewSet):
    """ViewSet for scan targets"""
    serializer_class = ScanTargetSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return ScanTarget.objects.none()
        return ScanTarget.objects.filter(organization=organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class SecurityScanViewSet(viewsets.ModelViewSet):
    """ViewSet for security scans"""
    serializer_class = SecurityScanSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return SecurityScan.objects.none()
        
        queryset = SecurityScan.objects.filter(organization=organization)
        
        # Filter by target if provided
        target_id = self.request.query_params.get('target')
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by scan type
        scan_type = self.request.query_params.get('scan_type')
        if scan_type:
            queryset = queryset.filter(scan_type=scan_type)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def create_scan(self, request):
        """Create and initiate a new scan"""
        target_id = request.data.get('target_id')
        scan_type = request.data.get('scan_type', 'full')
        
        if not target_id:
            return Response(
                {'error': 'target_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = ScannerService.create_scan(
            request.organization,
            target_id,
            scan_type
        )
        
        if result.get('success'):
            scan = SecurityScan.objects.get(id=result['scan_id'])
            serializer = self.get_serializer(scan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get detailed scan results"""
        scan = self.get_object()
        serializer = self.get_serializer(scan)
        return Response(serializer.data)


class VulnerabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for vulnerabilities"""
    serializer_class = VulnerabilitySerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return Vulnerability.objects.none()
        
        queryset = Vulnerability.objects.filter(scan__organization=organization)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by resolved status
        is_resolved = self.request.query_params.get('is_resolved')
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        # Filter by scan
        scan_id = self.request.query_params.get('scan')
        if scan_id:
            queryset = queryset.filter(scan_id=scan_id)
        
        return queryset.order_by('-severity', '-cvss_score')

