"""Management command to sync breaches from HaveIBeenPwned"""
from django.core.management.base import BaseCommand
from apps.breaches.services import BreachService


class Command(BaseCommand):
    help = 'Sync data breaches from HaveIBeenPwned API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-back',
            type=int,
            default=30,
            help='Number of days back to sync breaches (default: 30)',
        )

    def handle(self, *args, **options):
        days_back = options['days_back']
        
        self.stdout.write(f'Syncing breaches from HaveIBeenPwned (last {days_back} days)...')
        
        service = BreachService()
        result = service.sync_breaches_from_hibp(days_back=days_back)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSync completed:\n'
                f'  Fetched: {result["fetched"]}\n'
                f'  Created: {result["created"]}\n'
                f'  Updated: {result["updated"]}\n'
                f'  Errors: {result["errors"]}'
            )
        )








