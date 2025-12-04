from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    RansomwareGroupViewSet, RansomwareIncidentViewSet,
    RansomwareMonitorViewSet
)

router = DefaultRouter()
router.register(r'groups', RansomwareGroupViewSet, basename='ransomware-group')
router.register(r'incidents', RansomwareIncidentViewSet, basename='ransomware-incident')
router.register(r'monitors', RansomwareMonitorViewSet, basename='ransomware-monitor')

urlpatterns = [
    path('', include(router.urls)),
]

