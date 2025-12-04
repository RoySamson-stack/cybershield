from django.core.management.base import BaseCommand
from apps.monitoring.models import GitHubRepository


class Command(BaseCommand):
    help = 'Add a GitHub repository for monitoring'

    def add_arguments(self, parser):
        parser.add_argument('repo', type=str, help='Repository in format owner/repo (e.g., 0xMarcio/cve)')
        parser.add_argument(
            '--frequency',
            type=str,
            default='1hour',
            choices=['5min', '15min', '30min', '1hour', '6hours', '12hours', '24hours'],
            help='Monitoring frequency'
        )

    def handle(self, *args, **options):
        repo_full_name = options['repo']
        parts = repo_full_name.split('/')
        
        if len(parts) != 2:
            self.stdout.write(self.style.ERROR('Invalid repository format. Use: owner/repo'))
            return
        
        owner, repo_name = parts
        
        repo, created = GitHubRepository.objects.get_or_create(
            full_name=repo_full_name,
            defaults={
                'owner': owner,
                'repo_name': repo_name,
                'url': f'https://github.com/{repo_full_name}',
                'monitor_frequency': options['frequency'],
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully added repository: {repo_full_name}'))
        else:
            repo.monitor_frequency = options['frequency']
            repo.is_active = True
            repo.save()
            self.stdout.write(self.style.SUCCESS(f'Updated repository: {repo_full_name}'))

