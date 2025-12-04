"""
Celery Beat schedule configuration for monitoring tasks
Add this to your Django settings CELERY_BEAT_SCHEDULE
"""

CELERY_BEAT_SCHEDULE = {
    # Monitor GitHub repositories every hour
    'monitor-github-repositories': {
        'task': 'apps.monitoring.tasks.monitor_github_repositories',
        'schedule': 3600.0,  # Every hour
    },
    
    # Scrape ransomware.live every 6 hours
    'scrape-ransomware-live': {
        'task': 'apps.monitoring.tasks.scrape_ransomware_live',
        'schedule': 21600.0,  # Every 6 hours
    },
    
    # Monitor ransomware sites every hour
    'monitor-ransomware-sites': {
        'task': 'apps.monitoring.tasks.monitor_ransomware_sites',
        'schedule': 3600.0,  # Every hour
    },
    
    # Sync breaches from HaveIBeenPwned daily
    'sync-breaches-from-hibp': {
        'task': 'apps.monitoring.tasks.sync_breaches_from_hibp',
        'schedule': 86400.0,  # Every 24 hours
    },
    
    # Monitor breach alerts every 6 hours
    'monitor-breach-alerts': {
        'task': 'apps.monitoring.tasks.monitor_breach_alerts',
        'schedule': 21600.0,  # Every 6 hours
    },
    
    # Scan phishing domains every 4 hours
    'scan-phishing-domains': {
        'task': 'apps.monitoring.tasks.scan_phishing_domains',
        'schedule': 14400.0,  # Every 4 hours
    },
    
    # Monitor ransomware groups every 2 hours
    'monitor-ransomware-groups': {
        'task': 'apps.monitoring.tasks.monitor_ransomware_groups',
        'schedule': 7200.0,  # Every 2 hours
    },
    
    # Run scheduled security scans every hour
    'run-scheduled-scans': {
        'task': 'apps.monitoring.tasks.run_scheduled_scans',
        'schedule': 3600.0,  # Every hour
    },
    
    # Learn threat patterns daily
    'learn-threat-patterns': {
        'task': 'apps.monitoring.tasks.learn_threat_patterns',
        'schedule': 86400.0,  # Every 24 hours
    },
    
    # Generate threat intelligence every 6 hours
    'generate-threat-intelligence': {
        'task': 'apps.monitoring.tasks.generate_threat_intelligence',
        'schedule': 21600.0,  # Every 6 hours
    },
    
    # Analyze pending malware samples every hour
    'analyze-pending-samples': {
        'task': 'apps.monitoring.tasks.analyze_pending_samples',
        'schedule': 3600.0,  # Every hour
    },
}

