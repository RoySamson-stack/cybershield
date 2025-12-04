from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    GitHubRepositoryViewSet, GitHubCVERefViewSet,
    RansomwareSiteViewSet, RansomwarePostViewSet
)

router = DefaultRouter()
router.register(r'github-repos', GitHubRepositoryViewSet, basename='github-repo')
router.register(r'github-cve-refs', GitHubCVERefViewSet, basename='github-cve-ref')
router.register(r'ransomware-sites', RansomwareSiteViewSet, basename='ransomware-site')
router.register(r'ransomware-posts', RansomwarePostViewSet, basename='ransomware-post')

urlpatterns = [
    path('', include(router.urls)),
]

