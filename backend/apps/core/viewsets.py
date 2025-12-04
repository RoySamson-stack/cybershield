from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import date, timedelta

from .models import Organization, Subscription, APIKey, UsageMetrics, AuditLog
from .serializers import (
    OrganizationSerializer, OrganizationCreateSerializer,
    SubscriptionSerializer, APIKeySerializer, APIKeyCreateSerializer,
    UsageMetricsSerializer, AuditLogSerializer
)
from .permissions import IsOrganizationMember, IsOrganizationOwner, HasAPIAccess
from .utils import generate_api_key, track_usage, check_usage_limit


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for organization management"""
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(members=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get organization statistics"""
        organization = self.get_object()
        
        # Usage statistics
        today = date.today()
        usage_stats = UsageMetrics.objects.filter(
            organization=organization,
            date__year=today.year,
            date__month=today.month
        ).values('metric_type').annotate(total=Sum('count'))
        
        stats = {
            'subscription': SubscriptionSerializer(organization.subscription).data if organization.subscription else None,
            'usage': {item['metric_type']: item['total'] for item in usage_stats},
            'api_keys': APIKey.objects.filter(organization=organization, is_active=True).count(),
            'members': organization.members.count(),
        }
        
        return Response(stats)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subscription management"""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subscription.objects.all()
        if hasattr(user, 'organization') and user.organization:
            return Subscription.objects.filter(organization=user.organization)
        return Subscription.objects.none()
    
    @action(detail=False, methods=['get'])
    def available_plans(self, request):
        """Get all available subscription plans"""
        plans = Subscription.objects.filter(status='active').values(
            'plan_type', 'billing_cycle', 'price',
            'max_scans_per_month', 'max_api_requests_per_month',
            'max_monitored_domains', 'has_api_access', 'has_webhooks'
        ).distinct()
        
        return Response(list(plans))
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel subscription at period end"""
        subscription = self.get_object()
        subscription.cancel_at_period_end = True
        subscription.save()
        
        return Response({
            'message': 'Subscription will be cancelled at the end of the current period',
            'cancel_at_period_end': subscription.current_period_end
        })


class APIKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for API key management"""
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return APIKey.objects.none()
        return APIKey.objects.filter(organization=organization)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check API key limit
        organization = request.organization
        current_count = self.get_queryset().filter(is_active=True).count()
        if current_count >= organization.max_api_keys:
            return Response(
                {'error': f'Maximum API keys limit ({organization.max_api_keys}) reached'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate API key
        key, key_prefix = generate_api_key()
        
        api_key = APIKey.objects.create(
            organization=organization,
            created_by=request.user,
            key=key,
            key_prefix=key_prefix,
            **serializer.validated_data
        )
        
        # Return response with full key (only shown once)
        response_serializer = APIKeySerializer(api_key, context={'show_full_key': True})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke an API key"""
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        
        return Response({'message': 'API key revoked successfully'})
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate an API key (creates new, revokes old)"""
        old_key = self.get_object()
        
        # Generate new key
        key, key_prefix = generate_api_key()
        
        new_key = APIKey.objects.create(
            organization=old_key.organization,
            created_by=request.user,
            key=key,
            key_prefix=key_prefix,
            name=f"{old_key.name} (Regenerated)",
            rate_limit_per_hour=old_key.rate_limit_per_hour,
            scopes=old_key.scopes,
            expires_at=old_key.expires_at
        )
        
        # Revoke old key
        old_key.is_active = False
        old_key.save()
        
        response_serializer = APIKeySerializer(new_key, context={'show_full_key': True})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class UsageMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for usage metrics"""
    serializer_class = UsageMetricsSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return UsageMetrics.objects.none()
        
        queryset = UsageMetrics.objects.filter(organization=organization)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        metric_type = self.request.query_params.get('metric_type')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        return queryset.order_by('-date', '-created_at')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get usage summary for current period"""
        organization = request.organization
        if not organization:
            return Response({'error': 'No organization found'}, status=status.HTTP_400_BAD_REQUEST)
        
        today = date.today()
        subscription = organization.subscription
        
        # Get usage for current month
        usage = UsageMetrics.objects.filter(
            organization=organization,
            date__year=today.year,
            date__month=today.month
        ).values('metric_type').annotate(total=Sum('count'))
        
        usage_dict = {item['metric_type']: item['total'] for item in usage}
        
        # Get limits
        limits = {}
        if subscription:
            limits = {
                'scans': {
                    'used': usage_dict.get('scan', 0),
                    'limit': subscription.max_scans_per_month,
                    'unlimited': subscription.max_scans_per_month == -1
                },
                'api_requests': {
                    'used': usage_dict.get('api_request', 0),
                    'limit': subscription.max_api_requests_per_month,
                    'unlimited': subscription.max_api_requests_per_month == -1
                }
            }
        
        return Response({
            'period': {
                'start': date(today.year, today.month, 1).isoformat(),
                'end': (date(today.year, today.month + 1, 1) - timedelta(days=1)).isoformat()
            },
            'usage': usage_dict,
            'limits': limits
        })


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs"""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        organization = self.request.organization
        if not organization:
            return AuditLog.objects.none()
        
        queryset = AuditLog.objects.filter(organization=organization)
        
        # Filter by action type if provided
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')

