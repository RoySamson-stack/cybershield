"""Management command to scan a domain for phishing"""
from django.core.management.base import BaseCommand
from apps.phishing.services import PhishingService


class Command(BaseCommand):
    help = 'Scan a domain for phishing indicators'

    def add_arguments(self, parser):
        parser.add_argument(
            'domain',
            type=str,
            help='Domain to scan',
        )
        parser.add_argument(
            '--target-brand',
            type=str,
            default=None,
            help='Target brand name for similarity checking',
        )

    def handle(self, *args, **options):
        domain = options['domain']
        target_brand = options.get('target_brand')
        
        self.stdout.write(f'Scanning domain: {domain}...')
        
        service = PhishingService()
        result = service.scan_domain(domain, target_brand)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nScan Results:\n'
                f'  Domain: {result["domain"]}\n'
                f'  Is Phishing: {result["is_phishing"]}\n'
                f'  Threat Level: {result["threat_level"]}\n'
                f'  Reputation Score: {result["reputation"]["reputation_score"]}\n'
                f'  Is Suspicious: {result["reputation"]["is_suspicious"]}'
            )
        )
        
        if result.get('recommendations'):
            self.stdout.write('\nRecommendations:')
            for rec in result['recommendations']:
                self.stdout.write(f'  - {rec}')





