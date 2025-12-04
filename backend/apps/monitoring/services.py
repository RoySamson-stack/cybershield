import logging
from datetime import datetime
from typing import Optional, Dict, Any

from django.utils import timezone

from .models import (
    GitHubRepository,
    GitHubCVERef,
    RansomwareSite,
)
from .scrapers import GitHubScraper, RansomwareLiveScraper

logger = logging.getLogger(__name__)


def _parse_iso_datetime(value: str) -> datetime:
    """Convert an ISO string to an aware datetime."""
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if timezone.is_aware(parsed):
        return parsed
    return timezone.make_aware(parsed)


def monitor_github_repository_sync(
    repo: GitHubRepository,
    *,
    scraper: Optional[GitHubScraper] = None,
    log: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
    """Fetch latest commits/CVE references for a single repository."""
    log = log or logger
    scraper = scraper or GitHubScraper()

    stats = {
        'repo': repo.full_name,
        'new_commit': False,
        'cve_refs_created': 0,
        'error': None,
    }

    try:
        latest_commit = scraper.get_latest_commit(
            repo.owner,
            repo.repo_name,
            repo.default_branch,
        )

        if not latest_commit:
            repo.consecutive_failures += 1
            repo.check_error = "Failed to fetch latest commit"
            repo.last_check_at = timezone.now()
            repo.save(update_fields=['consecutive_failures', 'check_error', 'last_check_at'])
            stats['error'] = repo.check_error
            return stats

        # Only process if there is a new commit
        if repo.last_commit_sha != latest_commit['sha']:
            stats['new_commit'] = True
            since = repo.last_commit_date.isoformat() if repo.last_commit_date else None
            cve_refs = scraper.search_cve_in_repo(
                repo.owner,
                repo.repo_name,
                since,
            )

            for cve_ref in cve_refs:
                _, created = GitHubCVERef.objects.update_or_create(
                    repository=repo,
                    cve_id=cve_ref['cve_id'],
                    commit_sha=cve_ref['commit_sha'],
                    defaults={
                        'file_path': cve_ref.get('file_path', ''),
                        'commit_date': _parse_iso_datetime(cve_ref['commit_date']),
                        'commit_message': cve_ref.get('commit_message', ''),
                        'url': cve_ref.get('url', ''),
                        'is_new': True,
                    },
                )
                if created:
                    stats['cve_refs_created'] += 1

            repo.last_commit_sha = latest_commit['sha']
            repo.last_commit_date = _parse_iso_datetime(latest_commit['date'])
            repo.total_commits += 1
            repo.total_cves_found = GitHubCVERef.objects.filter(repository=repo).count()

        repo.last_check_at = timezone.now()
        repo.last_successful_check = timezone.now()
        repo.check_error = None
        repo.consecutive_failures = 0
        repo.save()
        log.info("Successfully monitored %s", repo.full_name)
        return stats

    except Exception as exc:  # pylint: disable=broad-except
        log.error("Error monitoring repository %s: %s", repo.full_name, exc)
        repo.consecutive_failures += 1
        repo.check_error = str(exc)
        repo.last_check_at = timezone.now()
        repo.save(update_fields=['consecutive_failures', 'check_error', 'last_check_at'])
        stats['error'] = repo.check_error
        return stats


def monitor_github_repositories_sync(*, log: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Process every active repository synchronously."""
    log = log or logger
    repos = GitHubRepository.objects.filter(is_active=True)
    scraper = GitHubScraper()
    summary = {
        'total_repositories': repos.count(),
        'processed': 0,
        'new_commits': 0,
        'cve_refs_created': 0,
        'failures': 0,
    }

    for repo in repos:
        result = monitor_github_repository_sync(repo, scraper=scraper, log=log)
        summary['processed'] += 1
        summary['cve_refs_created'] += result['cve_refs_created']
        if result['new_commit']:
            summary['new_commits'] += 1
        if result['error']:
            summary['failures'] += 1

    return summary


def scrape_ransomware_live_sync(*, log: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Fetch ransomware.live data synchronously and persist results."""
    log = log or logger
    scraper = RansomwareLiveScraper()
    sites = scraper.scrape_all_sites()

    summary = {
        'groups_discovered': 0,
        'records_processed': 0,
        'created': 0,
        'updated': 0,
        'errors': 0,
    }

    if not sites:
        log.warning("No ransomware.live data returned by scraper")
        return summary

    processed_groups = set()
    for site_data in sites:
        summary['records_processed'] += 1
        processed_groups.add(site_data.get('group_name'))
        try:
            _, created = RansomwareSite.objects.update_or_create(
                onion_address=site_data['onion_address'],
                defaults={
                    'group_name': site_data['group_name'],
                    'clearnet_url': site_data.get('clearnet_url'),
                    'site_name': site_data.get('site_name', site_data['group_name']),
                    'status': site_data.get('status', 'active'),
                    'is_active': site_data.get('status') != 'seized',
                    'source': site_data.get('source', 'ransomware.live'),
                    'source_url': site_data.get('source_url'),
                    'metadata': site_data.get('metadata', {}),
                    'last_checked_at': timezone.now(),
                    'last_successful_check': timezone.now(),
                },
            )
            if created:
                summary['created'] += 1
            else:
                summary['updated'] += 1
        except Exception as exc:  # pylint: disable=broad-except
            log.error("Error saving ransomware site %s: %s", site_data.get('onion_address'), exc)
            summary['errors'] += 1

    summary['groups_discovered'] = len(processed_groups)
    return summary

