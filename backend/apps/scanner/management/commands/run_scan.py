"""Management command to run a security scan"""
from django.core.management.base import BaseCommand
from apps.scanner.models import ScanTarget
from apps.scanner.services import ScannerService


class Command(BaseCommand):
    help = 'Run a security scan for a target'

    def add_arguments(self, parser):
        parser.add_argument(
            'target_id',
            type=str,
            help='UUID of the scan target',
        )
        parser.add_argument(
            '--scan-type',
            type=str,
            default='full',
            choices=['ssl', 'port', 'web', 'vulnerability', 'full'],
            help='Type of scan to perform',
        )

    def handle(self, *args, **options):
        target_id = options['target_id']
        scan_type = options['scan_type']
        
        try:
            target = ScanTarget.objects.get(id=target_id)
        except ScanTarget.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Target {target_id} not found')
            )
            return
        
        self.stdout.write(
            f'Running {scan_type} scan for target: {target.name} ({target.target_value})...'
        )
        
        result = ScannerService.create_scan(
            target.organization,
            target.id,
            scan_type=scan_type
        )
        
        if result.get('success'):
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nScan completed successfully!\n'
                    f'  Scan ID: {result["scan_id"]}\n'
                    f'  Status: {result["status"]}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Scan failed: {result.get("error", "Unknown error")}')
            )








