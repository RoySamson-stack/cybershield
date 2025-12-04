from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import C2Server, OnionSite, OnionDataPost, LeakedCredential, ThreatIntelligence
from .serializers import (
    C2ServerSerializer, OnionSiteSerializer, OnionDataPostSerializer,
    LeakedCredentialSerializer, ThreatIntelligenceSerializer
)
from apps.core.permissions import IsOrganizationMember


class OrganizationScopedModelViewSet(viewsets.ModelViewSet):
    """Base viewset that scopes data to the user's organization but allows global entries."""
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def filter_by_organization(self, queryset):
        organization_id = getattr(self.request.user, 'organization_id', None)
        if organization_id:
            return queryset.filter(
                Q(organization__isnull=True) | Q(organization_id=organization_id)
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(organization=getattr(self.request.user, 'organization', None))


class C2ServerViewSet(OrganizationScopedModelViewSet):
    """ViewSet for C2 servers"""
    serializer_class = C2ServerSerializer
    queryset = C2Server.objects.all()
    
    def get_queryset(self):
        queryset = self.filter_by_organization(self.queryset)
        
        # Filter by threat level
        threat_level = self.request.query_params.get('threat_level')
        if threat_level:
            queryset = queryset.filter(threat_level=threat_level)
        
        # Filter by C2 family
        c2_family = self.request.query_params.get('c2_family')
        if c2_family:
            queryset = queryset.filter(c2_family=c2_family)
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country=country)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-last_seen', '-threat_level')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get C2 server statistics"""
        scoped_queryset = self.filter_by_organization(C2Server.objects.all())
        stats = {
            'total': scoped_queryset.count(),
            'active': scoped_queryset.filter(is_active=True).count(),
            'by_family': list(scoped_queryset.values('c2_family').annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
            'by_country': list(scoped_queryset.values('country').annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
            'by_threat_level': list(scoped_queryset.values('threat_level').annotate(
                count=Count('id')
            )),
        }
        return Response(stats)


class OnionSiteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for onion sites"""
    serializer_class = OnionSiteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = OnionSite.objects.all()
        
        # Filter by site type
        site_type = self.request.query_params.get('site_type')
        if site_type:
            queryset = queryset.filter(site_type=site_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-last_checked', '-first_seen')
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get data posts for an onion site"""
        onion_site = self.get_object()
        posts = OnionDataPost.objects.filter(onion_site=onion_site).order_by('-posted_date')
        serializer = OnionDataPostSerializer(posts, many=True)
        return Response(serializer.data)


class OnionDataPostViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for onion data posts"""
    serializer_class = OnionDataPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = OnionDataPost.objects.all()
        
        # Filter by onion site
        onion_site = self.request.query_params.get('onion_site')
        if onion_site:
            queryset = queryset.filter(onion_site_id=onion_site)
        
        # Filter by affected organization
        org = self.request.query_params.get('organization')
        if org:
            queryset = queryset.filter(affected_organization__icontains=org)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(posted_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(posted_date__lte=end_date)
        
        return queryset.order_by('-posted_date', '-discovered_date')


class LeakedCredentialViewSet(OrganizationScopedModelViewSet):
    """ViewSet for leaked credentials"""
    serializer_class = LeakedCredentialSerializer
    queryset = LeakedCredential.objects.all()
    
    def get_queryset(self):
        queryset = self.filter_by_organization(self.queryset)
        
        # Filter by email
        email = self.request.query_params.get('email')
        if email:
            queryset = queryset.filter(email__icontains=email)
        
        # Filter by domain
        domain = self.request.query_params.get('domain')
        if domain:
            queryset = queryset.filter(domain__icontains=domain)
        
        # Filter by breach source
        breach_source = self.request.query_params.get('breach_source')
        if breach_source:
            queryset = queryset.filter(breach_source__icontains=breach_source)
        
        # Filter by exposed status
        is_exposed = self.request.query_params.get('is_exposed')
        if is_exposed is not None:
            queryset = queryset.filter(is_exposed=is_exposed.lower() == 'true')
        
        return queryset.order_by('-discovered_date', '-leak_date')
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search for leaked credentials"""
        email = request.query_params.get('email')
        username = request.query_params.get('username')
        domain = request.query_params.get('domain')
        
        if not (email or username or domain):
            return Response({'error': 'Provide email, username, or domain'}, status=400)
        
        queryset = LeakedCredential.objects.all()
        if email:
            queryset = queryset.filter(email__icontains=email)
        if username:
            queryset = queryset.filter(username__icontains=username)
        if domain:
            queryset = queryset.filter(domain__icontains=domain)
        
        serializer = self.get_serializer(queryset[:100], many=True)  # Limit results
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get leaked credentials statistics"""
        scoped_queryset = self.filter_by_organization(LeakedCredential.objects.all())
        stats = {
            'total': scoped_queryset.count(),
            'exposed': scoped_queryset.filter(is_exposed=True).count(),
            'by_breach': list(scoped_queryset.values('breach_source').annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
            'by_domain': list(scoped_queryset.values('domain').annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
            'recent': scoped_queryset.filter(
                discovered_date__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }
        return Response(stats)


class ThreatIntelligenceViewSet(OrganizationScopedModelViewSet):
    """ViewSet for threat intelligence"""
    serializer_class = ThreatIntelligenceSerializer
    queryset = ThreatIntelligence.objects.all()
    
    def get_queryset(self):
        queryset = self.filter_by_organization(self.queryset)
        
        # Filter by threat type
        threat_type = self.request.query_params.get('threat_type')
        if threat_type:
            queryset = queryset.filter(threat_type=threat_type)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by verified status
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        return queryset.order_by('-severity', '-first_seen', '-created_at')
    
    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Get threat intelligence timeline"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        threats = self.filter_by_organization(
            ThreatIntelligence.objects.all()
        ).filter(
            first_seen__gte=start_date
        ).order_by('first_seen')
        
        serializer = self.get_serializer(threats, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """Get threat intelligence data for map visualization"""
        threats = self.filter_by_organization(
            ThreatIntelligence.objects.all()
        ).filter(
            affected_countries__len__gt=0
        ).values('affected_countries', 'severity', 'threat_type', 'first_seen')
        
        # Aggregate by country
        country_data = {}
        for threat in threats:
            for country in threat['affected_countries']:
                if country not in country_data:
                    country_data[country] = {
                        'country': country,
                        'threats': 0,
                        'critical': 0,
                        'high': 0,
                        'medium': 0,
                        'low': 0,
                    }
                country_data[country]['threats'] += 1
                country_data[country][threat['severity']] += 1
        
        return Response(list(country_data.values()))

