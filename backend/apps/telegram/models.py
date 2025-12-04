from django.db import models
from django.utils import timezone
import uuid
from apps.core.models import Organization, User


class TelegramUser(models.Model):
    """Telegram user integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_user'
    )
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    is_bot = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'telegram_users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} (@{self.username})" if self.username else f"User {self.telegram_id}"


class TelegramBotConfig(models.Model):
    """Telegram bot configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='telegram_bots'
    )
    bot_token = models.CharField(max_length=255)
    bot_username = models.CharField(max_length=255, blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'telegram_bot_configs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bot for {self.organization.name}"


class TelegramNotification(models.Model):
    """Telegram notifications sent"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='telegram_notifications'
    )
    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    message_type = models.CharField(max_length=50)  # alert, threat, scan, etc.
    message_text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'telegram_notifications'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Notification to {self.telegram_user} - {self.message_type}"

