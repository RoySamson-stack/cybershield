from django.core.management.base import BaseCommand
from django.conf import settings
from apps.telegram.bot import TelegramBot
from apps.telegram.handlers import TelegramBotHandler
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Telegram bot in polling mode'

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            type=str,
            help='Telegram bot token',
        )

    def handle(self, *args, **options):
        bot_token = options.get('token') or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        
        if not bot_token:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN not found. Set it in settings or use --token option.')
            )
            return
        
        bot = TelegramBot(bot_token)
        handler = TelegramBotHandler(bot)
        
        # Get bot info
        try:
            bot_info = bot.get_me()
            self.stdout.write(
                self.style.SUCCESS(f'Bot started: @{bot_info["result"]["username"]}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to get bot info: {e}')
            )
            return
        
        # Polling loop
        offset = None
        self.stdout.write(self.style.SUCCESS('Starting polling...'))
        
        while True:
            try:
                updates = bot.get_updates(offset=offset)
                
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        offset = update['update_id'] + 1
                        
                        if 'message' in update:
                            handler.handle_command(update)
                        elif 'callback_query' in update:
                            # Handle callback queries
                            pass
                
                time.sleep(1)  # Poll every second
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\nStopping bot...'))
                break
            except Exception as e:
                logger.error(f'Error in polling loop: {e}')
                time.sleep(5)  # Wait before retrying

