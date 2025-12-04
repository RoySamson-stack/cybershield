from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import ScanTargetViewSet, SecurityScanViewSet, VulnerabilityViewSet

router = DefaultRouter()
router.register(r'targets', ScanTargetViewSet, basename='scan-target')
router.register(r'scans', SecurityScanViewSet, basename='security-scan')
router.register(r'vulnerabilities', VulnerabilityViewSet, basename='vulnerability')

urlpatterns = [
    path('', include(router.urls)),
]

