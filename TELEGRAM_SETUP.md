# Telegram Bot Integration Setup

## Overview

CyberShield now includes a complete Telegram bot integration for:
- Secure authentication via Telegram
- Real-time threat notifications
- Alert management
- Threat intelligence updates
- Security scan results

## Features

### Telegram Login Theme
- Beautiful Telegram-inspired login page
- Blue gradient theme matching Telegram's design
- Secure and professional appearance
- Password visibility toggle
- Telegram authentication option

### Bot Commands
- `/start` - Start the bot and get welcome message
- `/help` - Show available commands
- `/status` - Check account status
- `/alerts` - View recent alerts
- `/threats` - View recent threats
- `/link` - Get account linking code

### Notifications
- Real-time threat alerts
- Security scan results
- Data breach notifications
- C2 server detections
- Leaked credential alerts

## Setup Instructions

### 1. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the bot token (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Configure Backend

Add to your `.env` file:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
```

Or add to `settings/base.py`:

```python
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default=None)
TELEGRAM_BOT_USERNAME = env('TELEGRAM_BOT_USERNAME', default=None)
```

### 3. Run Database Migrations

```bash
docker-compose exec backend python manage.py makemigrations telegram
docker-compose exec backend python manage.py migrate
```

### 4. Start the Bot

#### Option A: Polling Mode (Development)

```bash
docker-compose exec backend python manage.py run_telegram_bot
```

#### Option B: Webhook Mode (Production)

1. Set webhook URL:
```python
from apps.telegram.bot import TelegramBot
bot = TelegramBot('your_bot_token')
bot.set_webhook('https://yourdomain.com/api/v1/telegram/webhook/')
```

2. Ensure your server is accessible from the internet
3. The webhook will automatically handle updates

### 5. Link User Accounts

#### Via Dashboard (Recommended)

1. User logs into CyberShield dashboard
2. Navigates to Settings → Telegram
3. Clicks "Link Telegram Account"
4. Gets a linking code
5. Opens Telegram bot and sends the code
6. Account is linked

#### Via Bot Command

1. User opens Telegram bot
2. Sends `/link` command
3. Gets a linking code
4. Enters code in dashboard
5. Account is linked

## Usage

### For Users

1. **Link Account**:
   - Go to `/auth/telegram` or use `/link` in bot
   - Follow the linking process

2. **Receive Notifications**:
   - Once linked, you'll automatically receive:
     - Threat alerts
     - Security scan results
     - Data breach notifications
     - C2 server detections

3. **Use Bot Commands**:
   - `/status` - Check your account
   - `/alerts` - View recent alerts
   - `/threats` - View recent threats

### For Developers

#### Send Notification Programmatically

```python
from apps.telegram.bot import TelegramBot
from apps.telegram.models import TelegramUser

# Get user's Telegram account
telegram_user = TelegramUser.objects.get(user=user)

# Send notification
bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
bot.send_alert(
    chat_id=telegram_user.telegram_id,
    alert_title="New Threat Detected",
    alert_message="A critical threat has been detected in your network.",
    severity="critical"
)
```

#### Send Threat Intelligence

```python
bot.send_threat_intelligence(
    chat_id=telegram_user.telegram_id,
    threat_title="New Ransomware Campaign",
    threat_description="A new ransomware campaign targeting healthcare organizations...",
    threat_type="ransomware",
    severity="high"
)
```

## API Endpoints

### Link Account
```
POST /api/v1/telegram/link/
Body: { "code": "linking_code" }
```

### Get Linking Code
```
GET /api/v1/telegram/link-code/
Returns: { "code": "...", "expires_in": 600 }
```

### Send Test Notification
```
POST /api/v1/telegram/test/
Sends a test notification to user's Telegram
```

### Webhook (Telegram)
```
POST /api/v1/telegram/webhook/
Handles Telegram updates
```

## Frontend Integration

### Login Page
- Beautiful Telegram-themed design
- Blue gradient background
- Secure password input
- Telegram login button

### Telegram Auth Page
- `/auth/telegram` - Link Telegram account
- Shows linking code
- Instructions for linking
- Direct bot link

## Security Features

1. **Secure Linking**:
   - Time-limited linking codes (10 minutes)
   - One-time use codes
   - User verification required

2. **Privacy**:
   - Telegram IDs stored securely
   - No sensitive data in messages
   - Encrypted communications

3. **Access Control**:
   - Only linked users receive notifications
   - Organization-based access
   - Role-based permissions

## Troubleshooting

### Bot Not Responding

1. Check bot token is correct
2. Verify bot is running (polling or webhook)
3. Check logs for errors
4. Ensure webhook URL is accessible (if using webhook)

### Linking Not Working

1. Verify linking code hasn't expired (10 minutes)
2. Check user is authenticated
3. Ensure Telegram user exists
4. Check database for TelegramUser records

### Notifications Not Sending

1. Verify user has linked Telegram account
2. Check TelegramUser.is_active is True
3. Verify bot token is valid
4. Check network connectivity
5. Review error logs

## Example Bot Conversation

```
User: /start
Bot: 👋 Welcome to CyberShield, John!

To get started, you need to link your Telegram account...

User: /link
Bot: 🔗 Account Linking

Your linking code is:
ABC123XYZ456

1. Go to CyberShield dashboard
2. Navigate to Settings → Telegram
3. Enter this code to link your account

User: /status
Bot: 📊 Account Status

User: john@example.com
Organization: Acme Corp
Role: owner
Subscription: professional
```

## Production Deployment

1. **Use Webhooks** (not polling) for production
2. **Set up SSL** for webhook endpoint
3. **Configure rate limiting** for webhook
4. **Monitor bot performance**
5. **Set up error alerts**
6. **Backup TelegramUser data**

## Next Steps

- [ ] Add more bot commands
- [ ] Implement callback query handlers
- [ ] Add inline keyboards for quick actions
- [ ] Create notification preferences
- [ ] Add scheduled reports
- [ ] Implement bot analytics

---

**Status**: ✅ Complete and ready for use!

