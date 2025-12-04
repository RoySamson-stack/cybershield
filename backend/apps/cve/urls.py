from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import CVEViewSet, CVECommentViewSet

router = DefaultRouter()
router.register(r'cves', CVEViewSet, basename='cve')
router.register(r'comments', CVECommentViewSet, basename='cve-comment')

urlpatterns = [
    path('', include(router.urls)),
]

