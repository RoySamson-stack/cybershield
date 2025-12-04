"""Telegram bot command handlers"""
from .bot import TelegramBot
from .models import TelegramUser, TelegramNotification
from apps.core.models import User, Organization
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    """Handle Telegram bot commands and messages"""
    
    def __init__(self, bot: TelegramBot):
        self.bot = bot
    
    def handle_command(self, update: dict) -> None:
        """Handle incoming command"""
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        from_user = message.get("from", {})
        
        if not text.startswith("/"):
            return
        
        command = text.split()[0].lower()
        
        try:
            if command == "/start":
                self.handle_start(chat_id, from_user)
            elif command == "/help":
                self.handle_help(chat_id)
            elif command == "/status":
                self.handle_status(chat_id, from_user)
            elif command == "/alerts":
                self.handle_alerts(chat_id, from_user)
            elif command == "/threats":
                self.handle_threats(chat_id, from_user)
            elif command == "/link":
                self.handle_link(chat_id, from_user)
            else:
                self.bot.send_message(chat_id, "Unknown command. Use /help for available commands.")
        except Exception as e:
            logger.error(f"Error handling command {command}: {e}")
            self.bot.send_message(chat_id, "An error occurred. Please try again later.")
    
    def handle_start(self, chat_id: int, from_user: dict) -> None:
        """Handle /start command"""
        telegram_id = from_user.get("id")
        username = from_user.get("username")
        first_name = from_user.get("first_name", "")
        
        # Check if user exists
        telegram_user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        
        if telegram_user:
            message = f"""
👋 Welcome back, {first_name}!

You're already linked to your CyberShield account.
Use /help to see available commands.
            """
        else:
            message = f"""
👋 Welcome to CyberShield, {first_name}!

To get started, you need to link your Telegram account to your CyberShield account.

1. Go to your CyberShield dashboard
2. Navigate to Settings → Telegram
3. Click "Link Telegram Account"
4. Use the code provided here

Or use /link to get your linking code.
            """
        
        self.bot.send_message(chat_id, message.strip())
    
    def handle_help(self, chat_id: int) -> None:
        """Handle /help command"""
        message = """
📚 <b>Available Commands:</b>

/start - Start the bot
/help - Show this help message
/status - Check your account status
/alerts - View recent alerts
/threats - View recent threats
/link - Get account linking code

<b>Features:</b>
• Real-time threat notifications
• Alert management
• Threat intelligence updates
• Security scan results
        """
        self.bot.send_message(chat_id, message.strip())
    
    def handle_status(self, chat_id: int, from_user: dict) -> None:
        """Handle /status command"""
        telegram_id = from_user.get("id")
        telegram_user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        
        if not telegram_user:
            self.bot.send_message(chat_id, "❌ Your Telegram account is not linked. Use /link to get started.")
            return
        
        user = telegram_user.user
        org = user.organization
        
        message = f"""
📊 <b>Account Status</b>

<b>User:</b> {user.email}
<b>Organization:</b> {org.name if org else "None"}
<b>Role:</b> {user.role}
<b>Last Activity:</b> {telegram_user.last_activity.strftime("%Y-%m-%d %H:%M")}

<b>Subscription:</b> {org.subscription.plan_type if org and org.subscription else "None"}
        """
        
        self.bot.send_message(chat_id, message.strip())
    
    def handle_alerts(self, chat_id: int, from_user: dict) -> None:
        """Handle /alerts command"""
        telegram_id = from_user.get("id")
        telegram_user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        
        if not telegram_user:
            self.bot.send_message(chat_id, "❌ Your Telegram account is not linked. Use /link to get started.")
            return
        
        from apps.alerts.models import Alert
        alerts = Alert.objects.filter(
            organization=telegram_user.user.organization
        ).order_by('-created_at')[:5]
        
        if not alerts:
            self.bot.send_message(chat_id, "✅ No recent alerts.")
            return
        
        message = "🚨 <b>Recent Alerts:</b>\n\n"
        for alert in alerts:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }
            emoji = severity_emoji.get(alert.severity, "🟡")
            message += f"{emoji} <b>{alert.title}</b>\n{alert.message[:100]}...\n\n"
        
        self.bot.send_message(chat_id, message.strip())
    
    def handle_threats(self, chat_id: int, from_user: dict) -> None:
        """Handle /threats command"""
        telegram_id = from_user.get("id")
        telegram_user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        
        if not telegram_user:
            self.bot.send_message(chat_id, "❌ Your Telegram account is not linked. Use /link to get started.")
            return
        
        from apps.threats.models import ThreatIntelligence
        threats = ThreatIntelligence.objects.all().order_by('-created_at')[:5]
        
        if not threats:
            self.bot.send_message(chat_id, "✅ No recent threats.")
            return
        
        message = "🎯 <b>Recent Threats:</b>\n\n"
        for threat in threats:
            message += f"🛡️ <b>{threat.title}</b>\n"
            message += f"Type: {threat.threat_type} | Severity: {threat.severity}\n\n"
        
        self.bot.send_message(chat_id, message.strip())
    
    def handle_link(self, chat_id: int, from_user: dict) -> None:
        """Handle /link command - generate linking code"""
        telegram_id = from_user.get("id")
        
        # Generate a linking code (in production, use a more secure method)
        import secrets
        linking_code = secrets.token_urlsafe(16)
        
        # Store in cache or database temporarily
        from django.core.cache import cache
        cache_key = f"telegram_link_{linking_code}"
        cache.set(cache_key, {
            "telegram_id": telegram_id,
            "username": from_user.get("username"),
            "first_name": from_user.get("first_name"),
        }, 600)  # 10 minutes TTL
        
        message = f"""
🔗 <b>Account Linking</b>

Your linking code is:
<code>{linking_code}</code>

1. Go to CyberShield dashboard
2. Navigate to Settings → Telegram
3. Enter this code to link your account

This code expires in 10 minutes.
        """
        
        self.bot.send_message(chat_id, message.strip())

