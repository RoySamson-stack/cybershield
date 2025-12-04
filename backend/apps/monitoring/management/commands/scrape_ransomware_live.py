from django.core.management.base import BaseCommand
from apps.monitoring.tasks import scrape_ransomware_live as scrape_task
from apps.monitoring.services import scrape_ransomware_live_sync


class Command(BaseCommand):
    help = 'Scrape ransomware.live for onion sites'

    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            action='store_true',
            dest='use_queue',
            help='Queue the Celery task instead of running synchronously.',
        )

    def handle(self, *args, **options):
        if options['use_queue']:
            self.stdout.write('Queuing ransomware.live scrape via Celery...')
            scrape_task.delay()
            self.stdout.write(self.style.SUCCESS('Scrape task queued successfully.'))
            return

        self.stdout.write('Running ransomware.live scrape now...')
        summary = scrape_ransomware_live_sync()
        self.stdout.write(
            self.style.SUCCESS(
                f"Scrape completed: {summary['created']} created, "
                f"{summary['updated']} updated, {summary['errors']} errors."
            )
        )

