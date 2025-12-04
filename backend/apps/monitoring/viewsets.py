from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, Count
from .models import GitHubRepository, GitHubCVERef, RansomwareSite, RansomwarePost
from .serializers import (
    GitHubRepositorySerializer, GitHubCVERefSerializer,
    RansomwareSiteSerializer, RansomwarePostSerializer
)
from .tasks import scrape_ransomware_live, monitor_github_repository


def _testing_permission():
    """Return relaxed permissions when DISABLE_AUTH_FOR_TESTING is enabled."""
    return [AllowAny] if settings.DISABLE_AUTH_FOR_TESTING else [IsAuthenticated]


class GitHubRepositoryViewSet(viewsets.ModelViewSet):
    """ViewSet for GitHub repository monitoring"""
    serializer_class = GitHubRepositorySerializer
    permission_classes = _testing_permission()
    
    def get_queryset(self):
        queryset = GitHubRepository.objects.all()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def trigger_check(self, request, pk=None):
        """Manually trigger a check for this repository"""
        repo = self.get_object()
        monitor_github_repository.delay(str(repo.id))
        return Response({'message': 'Check queued successfully'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get monitoring statistics"""
        total = GitHubRepository.objects.count()
        active = GitHubRepository.objects.filter(is_active=True).count()
        total_cves = GitHubCVERef.objects.count()
        new_cves = GitHubCVERef.objects.filter(is_new=True).count()
        
        return Response({
            'total_repositories': total,
            'active_repositories': active,
            'total_cves_found': total_cves,
            'new_cves': new_cves,
        })


class GitHubCVERefViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CVE references from GitHub"""
    serializer_class = GitHubCVERefSerializer
    permission_classes = _testing_permission()
    
    def get_queryset(self):
        queryset = GitHubCVERef.objects.all()
        
        repository = self.request.query_params.get('repository')
        if repository:
            queryset = queryset.filter(repository_id=repository)
        
        cve_id = self.request.query_params.get('cve_id')
        if cve_id:
            queryset = queryset.filter(cve_id__icontains=cve_id)
        
        is_new = self.request.query_params.get('is_new')
        if is_new is not None:
            queryset = queryset.filter(is_new=is_new.lower() == 'true')
        
        return queryset.order_by('-commit_date')


class RansomwareSiteViewSet(viewsets.ModelViewSet):
    """ViewSet for ransomware sites"""
    serializer_class = RansomwareSiteSerializer
    permission_classes = _testing_permission()
    
    def get_queryset(self):
        queryset = RansomwareSite.objects.all()
        
        group_name = self.request.query_params.get('group_name')
        if group_name:
            queryset = queryset.filter(group_name__icontains=group_name)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        has_new_posts = self.request.query_params.get('has_new_posts')
        if has_new_posts is not None:
            queryset = queryset.filter(has_new_posts=has_new_posts.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def scrape_now(self, request):
        """Trigger immediate scrape of ransomware.live"""
        scrape_ransomware_live.delay()
        return Response({'message': 'Scrape task queued successfully'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get ransomware site statistics"""
        total = RansomwareSite.objects.count()
        active = RansomwareSite.objects.filter(is_active=True).count()
        by_status = RansomwareSite.objects.values('status').annotate(count=Count('id'))
        total_posts = RansomwarePost.objects.count()
        new_posts = RansomwarePost.objects.filter(is_new=True).count()
        
        return Response({
            'total_sites': total,
            'active_sites': active,
            'by_status': list(by_status),
            'total_posts': total_posts,
            'new_posts': new_posts,
        })


class RansomwarePostViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ransomware posts"""
    serializer_class = RansomwarePostSerializer
    permission_classes = _testing_permission()
    
    def get_queryset(self):
        queryset = RansomwarePost.objects.all()
        
        site = self.request.query_params.get('site')
        if site:
            queryset = queryset.filter(site_id=site)
        
        group_name = self.request.query_params.get('group_name')
        if group_name:
            queryset = queryset.filter(site__group_name__icontains=group_name)
        
        is_new = self.request.query_params.get('is_new')
        if is_new is not None:
            queryset = queryset.filter(is_new=is_new.lower() == 'true')
        
        return queryset.order_by('-posted_date', '-discovered_date')

