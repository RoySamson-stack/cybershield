"""Telegram webhook and API views"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging

from .bot import TelegramBot
from .handlers import TelegramBotHandler
from .models import TelegramUser, TelegramBotConfig, TelegramNotification
from apps.core.models import User

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def webhook(request):
    """Telegram webhook endpoint"""
    try:
        update = json.loads(request.body)
        
        # Get bot token from environment or config
        from django.conf import settings
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not configured")
            return JsonResponse({"ok": False, "error": "Bot token not configured"})
        
        bot = TelegramBot(bot_token)
        handler = TelegramBotHandler(bot)
        
        # Handle the update
        if "message" in update:
            handler.handle_command(update)
        elif "callback_query" in update:
            # Handle callback queries
            pass
        
        return JsonResponse({"ok": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JsonResponse({"ok": False, "error": str(e)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def link_account(request):
    """Link Telegram account to user"""
    linking_code = request.data.get('code')
    
    if not linking_code:
        return Response(
            {"error": "Linking code is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get linking data from cache
    from django.core.cache import cache
    cache_key = f"telegram_link_{linking_code}"
    link_data = cache.get(cache_key)
    
    if not link_data:
        return Response(
            {"error": "Invalid or expired linking code"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    telegram_id = link_data.get("telegram_id")
    
    # Create or update Telegram user
    telegram_user, created = TelegramUser.objects.update_or_create(
        telegram_id=telegram_id,
        defaults={
            "user": request.user,
            "username": link_data.get("username"),
            "first_name": link_data.get("first_name"),
            "is_active": True,
        }
    )
    
    # Clear the cache
    cache.delete(cache_key)
    
    return Response({
        "success": True,
        "message": "Telegram account linked successfully",
        "telegram_user": {
            "id": str(telegram_user.id),
            "telegram_id": telegram_user.telegram_id,
            "username": telegram_user.username,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_linking_code(request):
    """Get a new linking code for the user"""
    import secrets
    linking_code = secrets.token_urlsafe(16)
    
    # Store in cache
    from django.core.cache import cache
    cache_key = f"telegram_link_{linking_code}"
    cache.set(cache_key, {
        "user_id": request.user.id,
        "email": request.user.email,
    }, 600)  # 10 minutes
    
    return Response({
        "code": linking_code,
        "expires_in": 600,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_notification(request):
    """Send a test notification to user's Telegram"""
    telegram_user = TelegramUser.objects.filter(user=request.user, is_active=True).first()
    
    if not telegram_user:
        return Response(
            {"error": "Telegram account not linked"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from django.conf import settings
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    
    if not bot_token:
        return Response(
            {"error": "Telegram bot not configured"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    bot = TelegramBot(bot_token)
    
    try:
        bot.send_message(
            telegram_user.telegram_id,
            "🧪 <b>Test Notification</b>\n\nThis is a test notification from CyberShield. Your Telegram integration is working!"
        )
        
        return Response({
            "success": True,
            "message": "Test notification sent"
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

