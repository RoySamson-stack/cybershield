from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import CVE, CVEComment
from .serializers import CVESerializer, CVECommentSerializer


def _testing_permissions():
    """Return relaxed permissions when auth bypass flag is enabled."""
    return [AllowAny] if getattr(settings, 'DISABLE_AUTH_FOR_TESTING', False) else [IsAuthenticated]


class CVEViewSet(viewsets.ModelViewSet):
    """ViewSet for CVE management"""
    serializer_class = CVESerializer
    permission_classes = _testing_permissions()
    
    def get_queryset(self):
        queryset = CVE.objects.all()
        
        # Filtering
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        has_exploit = self.request.query_params.get('has_exploit')
        if has_exploit == 'true':
            queryset = queryset.filter(has_exploit=True)
        
        poc_available = self.request.query_params.get('poc_available')
        if poc_available == 'true':
            queryset = queryset.filter(poc_available=True)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        vendor = self.request.query_params.get('vendor')
        if vendor:
            queryset = queryset.filter(vendor__icontains=vendor)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(cve_id__icontains=search) |
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(vendor__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-published_date')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def perform_create(self, serializer):
        """Attach organization and sharing user on create."""
        organization = getattr(self.request, 'organization', None)
        serializer.save(
            organization=organization,
            shared_by=self.request.user if self.request.user.is_authenticated else None,
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get CVE statistics"""
        total = CVE.objects.count()
        by_severity = CVE.objects.values('severity').annotate(count=Count('id'))
        by_status = CVE.objects.values('status').annotate(count=Count('id'))
        with_exploit = CVE.objects.filter(has_exploit=True).count()
        with_poc = CVE.objects.filter(poc_available=True).count()
        recent = CVE.objects.filter(
            published_date__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        avg_cvss = CVE.objects.aggregate(avg=Avg('cvss_v3_score'))['avg'] or 0
        
        return Response({
            'total': total,
            'recent_30_days': recent,
            'with_exploit': with_exploit,
            'with_poc': with_poc,
            'average_cvss': round(float(avg_cvss), 2),
            'by_severity': list(by_severity),
            'by_status': list(by_status),
        })
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest CVEs"""
        limit = int(request.query_params.get('limit', 20))
        cves = CVE.objects.order_by('-published_date', '-created_at')[:limit]
        serializer = self.get_serializer(cves, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        """Upvote a CVE"""
        cve = self.get_object()
        cve.upvotes += 1
        cve.save()
        return Response({'upvotes': cve.upvotes})
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get comments for a CVE"""
        cve = self.get_object()
        comments = cve.comments.all()
        serializer = CVECommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to a CVE"""
        cve = self.get_object()
        serializer = CVECommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cve=cve, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CVECommentViewSet(viewsets.ModelViewSet):
    """ViewSet for CVE comments"""
    serializer_class = CVECommentSerializer
    permission_classes = _testing_permissions()
    
    def get_queryset(self):
        return CVEComment.objects.all()
    
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        """Upvote a comment"""
        comment = self.get_object()
        comment.upvotes += 1
        comment.save()
        return Response({'upvotes': comment.upvotes})

