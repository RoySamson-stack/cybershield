from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    PhishingCampaignViewSet, PhishingDomainViewSet,
    PhishingMonitorViewSet
)

router = DefaultRouter()
router.register(r'campaigns', PhishingCampaignViewSet, basename='phishing-campaign')
router.register(r'domains', PhishingDomainViewSet, basename='phishing-domain')
router.register(r'monitors', PhishingMonitorViewSet, basename='phishing-monitor')

urlpatterns = [
    path('', include(router.urls)),
]

