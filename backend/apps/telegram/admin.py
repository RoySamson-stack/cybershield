from django.contrib import admin
from .models import TelegramUser, TelegramBotConfig, TelegramNotification


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_id', 'username', 'first_name', 'is_active', 'last_activity']
    list_filter = ['is_active', 'is_bot']
    search_fields = ['user__email', 'username', 'telegram_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TelegramBotConfig)
class TelegramBotConfigAdmin(admin.ModelAdmin):
    list_display = ['organization', 'bot_username', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['organization__name', 'bot_username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TelegramNotification)
class TelegramNotificationAdmin(admin.ModelAdmin):
    list_display = ['organization', 'telegram_user', 'message_type', 'is_sent', 'sent_at']
    list_filter = ['is_sent', 'message_type', 'sent_at']
    search_fields = ['organization__name', 'message_text']
    readonly_fields = ['id', 'sent_at']
    date_hierarchy = 'sent_at'

