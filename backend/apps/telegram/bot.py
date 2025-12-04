"""Telegram bot handler"""
import requests
import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot client"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[dict] = None
    ) -> dict:
        """Send a message to a Telegram chat"""
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            raise
    
    def send_alert(
        self,
        chat_id: int,
        alert_title: str,
        alert_message: str,
        severity: str = "medium"
    ) -> dict:
        """Send an alert notification"""
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
        }
        
        emoji = severity_emoji.get(severity, "🟡")
        text = f"{emoji} <b>{alert_title}</b>\n\n{alert_message}"
        
        return self.send_message(chat_id, text)
    
    def send_threat_intelligence(
        self,
        chat_id: int,
        threat_title: str,
        threat_description: str,
        threat_type: str,
        severity: str
    ) -> dict:
        """Send threat intelligence notification"""
        text = f"""
🛡️ <b>New Threat Detected</b>

<b>Title:</b> {threat_title}
<b>Type:</b> {threat_type}
<b>Severity:</b> {severity}

<b>Description:</b>
{threat_description}
        """
        
        return self.send_message(chat_id, text.strip())
    
    def get_me(self) -> dict:
        """Get bot information"""
        url = f"{self.api_url}/getMe"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            raise
    
    def set_webhook(self, webhook_url: str) -> dict:
        """Set webhook URL"""
        url = f"{self.api_url}/setWebhook"
        payload = {"url": webhook_url}
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            raise
    
    def get_updates(self, offset: Optional[int] = None) -> dict:
        """Get bot updates"""
        url = f"{self.api_url}/getUpdates"
        params = {}
        if offset:
            params["offset"] = offset
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            raise


def create_inline_keyboard(buttons: list) -> dict:
    """Create inline keyboard markup"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button in row:
            keyboard_row.append({
                "text": button["text"],
                "callback_data": button.get("callback_data", ""),
                "url": button.get("url"),
            })
        keyboard.append(keyboard_row)
    
    return {"inline_keyboard": keyboard}

