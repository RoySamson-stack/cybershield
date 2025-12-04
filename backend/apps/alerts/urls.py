from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import AlertRuleViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'rules', AlertRuleViewSet, basename='alert-rule')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]

