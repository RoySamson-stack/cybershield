from django.core.management.base import BaseCommand
from apps.monitoring.tasks import monitor_github_repositories as monitor_task
from apps.monitoring.services import monitor_github_repositories_sync


class Command(BaseCommand):
    help = 'Run GitHub repository monitoring immediately.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            action='store_true',
            dest='use_queue',
            help='Queue the Celery task instead of running synchronously.',
        )

    def handle(self, *args, **options):
        if options['use_queue']:
            self.stdout.write('Queuing GitHub monitoring task via Celery...')
            monitor_task.delay()
            self.stdout.write(self.style.SUCCESS('Monitoring task queued successfully.'))
            return

        self.stdout.write('Monitoring GitHub repositories now...')
        summary = monitor_github_repositories_sync()
        self.stdout.write(
            self.style.SUCCESS(
                f"Monitoring complete: {summary['processed']} repos, "
                f"{summary['new_commits']} new commits, "
                f"{summary['cve_refs_created']} CVE refs, "
                f"{summary['failures']} failures."
            )
        )

