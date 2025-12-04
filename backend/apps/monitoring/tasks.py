from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
import requests
from .models import GitHubRepository, RansomwareSite, RansomwarePost
from .services import (
    monitor_github_repositories_sync,
    monitor_github_repository_sync,
    scrape_ransomware_live_sync,
)

logger = logging.getLogger(__name__)


@shared_task
def monitor_github_repositories():
    """Monitor all active GitHub repositories for changes."""
    return monitor_github_repositories_sync(log=logger)


@shared_task
def monitor_github_repository(repo_id: str):
    """Monitor a specific GitHub repository."""
    try:
        repo = GitHubRepository.objects.get(id=repo_id)
    except GitHubRepository.DoesNotExist:
        logger.error("Repository %s not found", repo_id)
        return

    return monitor_github_repository_sync(repo, log=logger)


@shared_task
def scrape_ransomware_live():
    """Scrape ransomware.live for onion sites."""
    return scrape_ransomware_live_sync(log=logger)


@shared_task
def monitor_ransomware_sites():
    """Monitor all active ransomware sites for new posts"""
    sites = RansomwareSite.objects.filter(is_active=True)
    
    for site in sites:
        try:
            check_ransomware_site.delay(str(site.id))
        except Exception as e:
            logger.error(f"Error queuing check task for {site.onion_address}: {e}")


@shared_task
def check_ransomware_site(site_id: str):
    """Check a specific ransomware site for new posts"""
    try:
        site = RansomwareSite.objects.get(id=site_id)
        
        # This would require Tor/proxy setup to access .onion sites
        # For now, we'll just update the check timestamp
        # In production, you'd use something like:
        # - Stem library with Tor
        # - Proxy service
        # - Or scrape from clearnet mirrors if available
        
        site.last_checked_at = timezone.now()
        site.check_count += 1
        
        # If we have a clearnet URL, try to scrape it
        if site.clearnet_url:
            try:
                response = requests.get(site.clearnet_url, timeout=30)
                if response.status_code == 200:
                    # Parse and extract posts
                    # This would need BeautifulSoup parsing
                    site.last_successful_check = timezone.now()
                    site.consecutive_failures = 0
                else:
                    site.consecutive_failures += 1
            except Exception as e:
                logger.error(f"Error checking clearnet URL for {site.onion_address}: {e}")
                site.consecutive_failures += 1
        else:
            # Mark as checked but note we can't actually verify
            site.last_successful_check = timezone.now()
        
        site.save()
        
    except RansomwareSite.DoesNotExist:
        logger.error(f"Ransomware site {site_id} not found")
    except Exception as e:
        logger.error(f"Error checking ransomware site {site_id}: {e}")


# New tasks for enhanced data collection

@shared_task
def sync_breaches_from_hibp():
    """Sync data breaches from HaveIBeenPwned API"""
    try:
        from apps.breaches.services import BreachService
        
        service = BreachService()
        result = service.sync_breaches_from_hibp(days_back=30)
        logger.info(f"Breach sync completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error syncing breaches: {e}")
        return {'error': str(e)}


@shared_task
def monitor_breach_alerts():
    """Check breach monitors and generate alerts"""
    try:
        from apps.breaches.models import BreachMonitor
        from apps.breaches.services import BreachService
        from apps.core.models import Organization
        
        service = BreachService()
        
        monitors = BreachMonitor.objects.filter(is_active=True)
        summary = {
            'monitors_checked': 0,
            'alerts_generated': 0,
            'errors': 0
        }
        
        for monitor in monitors:
            try:
                result = service.monitor_organization_breaches(monitor.organization, monitor)
                summary['monitors_checked'] += 1
                summary['alerts_generated'] += result.get('alerts', 0)
                
                # TODO: Generate alerts if needed
                if result.get('alerts', 0) > 0:
                    logger.info(f"Generated {result['alerts']} alerts for monitor {monitor.id}")
                    
            except Exception as e:
                logger.error(f"Error monitoring breaches for {monitor.id}: {e}")
                summary['errors'] += 1
        
        return summary
    except Exception as e:
        logger.error(f"Error in breach monitoring task: {e}")
        return {'error': str(e)}


@shared_task
def scan_phishing_domains():
    """Scan domains for phishing detection"""
    try:
        from apps.phishing.models import PhishingMonitor
        from apps.phishing.services import PhishingService
        
        service = PhishingService()
        
        monitors = PhishingMonitor.objects.filter(is_active=True)
        summary = {
            'monitors_checked': 0,
            'domains_scanned': 0,
            'phishing_detected': 0,
            'errors': 0
        }
        
        for monitor in monitors:
            try:
                result = service.monitor_domains(monitor)
                summary['monitors_checked'] += 1
                summary['domains_scanned'] += result.get('scanned', 0)
                summary['phishing_detected'] += result.get('phishing_detected', 0)
            except Exception as e:
                logger.error(f"Error scanning phishing domains for monitor {monitor.id}: {e}")
                summary['errors'] += 1
        
        return summary
    except Exception as e:
        logger.error(f"Error in phishing scan task: {e}")
        return {'error': str(e)}


@shared_task
def monitor_ransomware_groups():
    """Monitor ransomware groups and check their sites"""
    try:
        from apps.ransomware.services import RansomwareService
        from apps.ransomware.models import RansomwareGroup
        
        service = RansomwareService(use_tor=True)
        
        groups = RansomwareGroup.objects.filter(is_active=True)
        summary = {
            'groups_checked': 0,
            'sites_checked': 0,
            'new_incidents': 0,
            'errors': 0
        }
        
        for group in groups:
            try:
                result = service.monitor_group_sites(group)
                summary['groups_checked'] += 1
                summary['sites_checked'] += result.get('sites_checked', 0)
                summary['new_incidents'] += result.get('new_incidents', 0)
            except Exception as e:
                logger.error(f"Error monitoring group {group.name}: {e}")
                summary['errors'] += 1
        
        return summary
    except Exception as e:
        logger.error(f"Error in ransomware monitoring task: {e}")
        return {'error': str(e)}


@shared_task
def run_scheduled_scans():
    """Run scheduled security scans"""
    try:
        from apps.scanner.models import ScanTarget
        from apps.scanner.services import ScannerService
        
        # Get targets that need scanning
        now = timezone.now()
        targets = ScanTarget.objects.filter(
            is_active=True,
            next_scan_at__lte=now
        )
        
        summary = {
            'targets_scanned': 0,
            'scans_completed': 0,
            'scans_failed': 0,
            'errors': 0
        }
        
        for target in targets:
            try:
                result = ScannerService.create_scan(
                    target.organization,
                    target.id,
                    scan_type='full'
                )
                
                if result.get('success'):
                    summary['scans_completed'] += 1
                    target.last_scan_at = now
                    # Calculate next scan time based on frequency
                    if target.scan_frequency == 'daily':
                        target.next_scan_at = now + timedelta(days=1)
                    elif target.scan_frequency == 'weekly':
                        target.next_scan_at = now + timedelta(weeks=1)
                    elif target.scan_frequency == 'monthly':
                        target.next_scan_at = now + timedelta(days=30)
                    target.save()
                else:
                    summary['scans_failed'] += 1
                
                summary['targets_scanned'] += 1
                
            except Exception as e:
                logger.error(f"Error running scan for target {target.id}: {e}")
                summary['errors'] += 1
        
        return summary
    except Exception as e:
        logger.error(f"Error in scheduled scans task: {e}")
        return {'error': str(e)}


# Malware analysis tasks

@shared_task
def learn_threat_patterns():
    """Learn threat patterns from collected malware samples"""
    try:
        from apps.malware.ml_service import ThreatPatternLearningService
        
        service = ThreatPatternLearningService()
        patterns = service.learn_patterns(days=30)
        
        # Update trends
        service.update_trends()
        
        logger.info(f"Learned {len(patterns)} threat patterns")
        return {
            'patterns_learned': len(patterns),
            'patterns': [p.pattern_name for p in patterns]
        }
    except Exception as e:
        logger.error(f"Error learning threat patterns: {e}")
        return {'error': str(e)}


@shared_task
def generate_threat_intelligence():
    """Generate threat intelligence from recent samples"""
    try:
        from apps.malware.services import ThreatIntelligenceService
        
        service = ThreatIntelligenceService()
        intelligence_items = service.generate_intelligence(days=7)
        
        logger.info(f"Generated {len(intelligence_items)} threat intelligence items")
        return {
            'intelligence_generated': len(intelligence_items),
            'items': [item.title for item in intelligence_items]
        }
    except Exception as e:
        logger.error(f"Error generating threat intelligence: {e}")
        return {'error': str(e)}


@shared_task
def analyze_pending_samples():
    """Analyze pending malware samples"""
    try:
        from apps.malware.models import MalwareSample
        from apps.malware.services import VirusTotalService, BehavioralAnalysisService
        
        pending_samples = MalwareSample.objects.filter(status='pending')[:10]
        
        vt_service = VirusTotalService()
        behavior_service = BehavioralAnalysisService()
        
        summary = {
            'analyzed': 0,
            'failed': 0,
            'errors': 0
        }
        
        for sample in pending_samples:
            try:
                sample.status = 'analyzing'
                sample.save()
                
                # VirusTotal analysis
                vt_service.analyze_sample(sample)
                
                # Behavioral analysis (if file stored)
                if sample.is_stored:
                    behavior_service.analyze_sample(sample)
                
                sample.status = 'completed'
                sample.analyzed_at = timezone.now()
                sample.save()
                
                summary['analyzed'] += 1
                
            except Exception as e:
                logger.error(f"Error analyzing sample {sample.id}: {e}")
                sample.status = 'failed'
                sample.save()
                summary['failed'] += 1
        
        return summary
    except Exception as e:
        logger.error(f"Error in analyze pending samples task: {e}")
        return {'error': str(e)}

