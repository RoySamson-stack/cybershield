from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    C2ServerViewSet, OnionSiteViewSet, OnionDataPostViewSet,
    LeakedCredentialViewSet, ThreatIntelligenceViewSet
)

router = DefaultRouter()
router.register(r'c2-servers', C2ServerViewSet, basename='c2-server')
router.register(r'onion-sites', OnionSiteViewSet, basename='onion-site')
router.register(r'onion-posts', OnionDataPostViewSet, basename='onion-post')
router.register(r'leaked-credentials', LeakedCredentialViewSet, basename='leaked-credential')
router.register(r'threat-intelligence', ThreatIntelligenceViewSet, basename='threat-intelligence')

urlpatterns = [
    path('', include(router.urls)),
]

