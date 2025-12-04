from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import DataBreachViewSet, BreachMonitorViewSet

router = DefaultRouter()
router.register(r'breaches', DataBreachViewSet, basename='data-breach')
router.register(r'monitors', BreachMonitorViewSet, basename='breach-monitor')

urlpatterns = [
    path('', include(router.urls)),
]

