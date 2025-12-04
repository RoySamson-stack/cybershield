from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .viewsets import (
    OrganizationViewSet, SubscriptionViewSet, APIKeyViewSet,
    UsageMetricsViewSet, AuditLogViewSet
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')
router.register(r'usage', UsageMetricsViewSet, basename='usage')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('metrics/', views.metrics, name='metrics'),
    path('', include(router.urls)),
]
