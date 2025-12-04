"""Services for data breach monitoring and aggregation"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .models import DataBreach, BreachMonitor
from apps.core.models import Organization

logger = logging.getLogger(__name__)


class BreachService:
    """Service for data breach monitoring and aggregation"""
    
    HIBP_API_BASE = "https://haveibeenpwned.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional HaveIBeenPwned API key"""
        self.api_key = api_key or getattr(settings, 'HIBP_API_KEY', None)
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'hibp-api-key': self.api_key,
                'User-Agent': 'CyberShield/1.0'
            })
        else:
            self.session.headers.update({
                'User-Agent': 'CyberShield/1.0'
            })
    
    def check_email(self, email: str) -> List[Dict]:
        """Check if an email has been breached using HaveIBeenPwned API"""
        breaches = []
        
        try:
            response = self.session.get(
                f"{self.HIBP_API_BASE}/breachedaccount/{email}",
                params={'truncateResponse': 'false'},
                timeout=10
            )
            
            if response.status_code == 200:
                breach_data = response.json()
                for breach in breach_data:
                    breaches.append({
                        'name': breach.get('Name', ''),
                        'title': breach.get('Title', ''),
                        'domain': breach.get('Domain', ''),
                        'breach_date': breach.get('BreachDate', ''),
                        'added_date': breach.get('AddedDate', ''),
                        'modified_date': breach.get('ModifiedDate', ''),
                        'pwn_count': breach.get('PwnCount', 0),
                        'description': breach.get('Description', ''),
                        'data_classes': breach.get('DataClasses', []),
                        'is_verified': breach.get('IsVerified', False),
                        'is_fabricated': breach.get('IsFabricated', False),
                        'is_sensitive': breach.get('IsSensitive', False),
                        'is_retired': breach.get('IsRetired', False),
                        'is_spam_list': breach.get('IsSpamList', False),
                        'logo_path': breach.get('LogoPath', ''),
                    })
            elif response.status_code == 404:
                logger.info(f"Email {email} not found in breaches")
            else:
                logger.warning(f"HIBP API returned status {response.status_code} for {email}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking email {email} with HIBP: {e}")
        except Exception as e:
            logger.error(f"Unexpected error checking email {email}: {e}")
        
        return breaches
    
    def get_all_breaches(self) -> List[Dict]:
        """Get all breaches from HaveIBeenPwned"""
        breaches = []
        
        try:
            response = self.session.get(
                f"{self.HIBP_API_BASE}/breaches",
                timeout=30
            )
            
            if response.status_code == 200:
                breach_data = response.json()
                for breach in breach_data:
                    breaches.append({
                        'name': breach.get('Name', ''),
                        'title': breach.get('Title', ''),
                        'domain': breach.get('Domain', ''),
                        'breach_date': breach.get('BreachDate', ''),
                        'added_date': breach.get('AddedDate', ''),
                        'modified_date': breach.get('ModifiedDate', ''),
                        'pwn_count': breach.get('PwnCount', 0),
                        'description': breach.get('Description', ''),
                        'data_classes': breach.get('DataClasses', []),
                        'is_verified': breach.get('IsVerified', False),
                        'is_fabricated': breach.get('IsFabricated', False),
                        'is_sensitive': breach.get('IsSensitive', False),
                        'is_retired': breach.get('IsRetired', False),
                        'is_spam_list': breach.get('IsSpamList', False),
                        'logo_path': breach.get('LogoPath', ''),
                    })
        except Exception as e:
            logger.error(f"Error fetching all breaches from HIBP: {e}")
        
        return breaches
    
    def sync_breaches_from_hibp(self, days_back: int = 30) -> Dict:
        """Sync breaches from HaveIBeenPwned to database"""
        summary = {
            'fetched': 0,
            'created': 0,
            'updated': 0,
            'errors': 0
        }
        
        try:
            all_breaches = self.get_all_breaches()
            summary['fetched'] = len(all_breaches)
            
            cutoff_date = timezone.now() - timedelta(days=days_back)
            
            for breach_data in all_breaches:
                try:
                    breach_date = None
                    if breach_data.get('breach_date'):
                        try:
                            breach_date = datetime.strptime(breach_data['breach_date'], '%Y-%m-%d').date()
                        except:
                            pass
                    
                    if breach_date and breach_date < cutoff_date.date():
                        continue
                    
                    severity = 'medium'
                    if breach_data.get('pwn_count', 0) > 10000000:
                        severity = 'critical'
                    elif breach_data.get('pwn_count', 0) > 1000000:
                        severity = 'high'
                    
                    data_classes = breach_data.get('data_classes', [])
                    if any(dc in data_classes for dc in ['Passwords', 'Credit cards', 'Bank account numbers']):
                        if severity == 'medium':
                            severity = 'high'
                    
                    affected_org = breach_data.get('domain', '')
                    if not affected_org:
                        affected_org = breach_data.get('title', '').split()[0] if breach_data.get('title') else 'Unknown'
                    
                    breach, created = DataBreach.objects.update_or_create(
                        breach_name=breach_data.get('name', ''),
                        defaults={
                            'affected_organization': affected_org,
                            'breach_date': breach_date,
                            'discovered_date': breach_date,
                            'records_affected': breach_data.get('pwn_count', 0),
                            'data_types': data_classes,
                            'breach_type': 'hack',
                            'severity': severity,
                            'description': breach_data.get('description', ''),
                            'source_url': f"https://haveibeenpwned.com/PwnedWebsites#{breach_data.get('name', '')}",
                            'is_verified': breach_data.get('is_verified', False),
                            'metadata': {
                                'hibp_name': breach_data.get('name', ''),
                                'hibp_title': breach_data.get('title', ''),
                                'added_date': breach_data.get('added_date', ''),
                                'modified_date': breach_data.get('modified_date', ''),
                                'logo_path': breach_data.get('logo_path', ''),
                            }
                        }
                    )
                    
                    if created:
                        summary['created'] += 1
                    else:
                        summary['updated'] += 1
                        
                except Exception as e:
                    logger.error(f"Error syncing breach {breach_data.get('name', 'unknown')}: {e}")
                    summary['errors'] += 1
                    
        except Exception as e:
            logger.error(f"Error syncing breaches from HIBP: {e}")
            summary['errors'] += 1
        
        return summary
    
    def monitor_organization_breaches(self, organization: Organization, monitor: BreachMonitor) -> Dict:
        """Monitor breaches for an organization based on monitor settings"""
        summary = {
            'checked': 0,
            'matches': 0,
            'alerts': 0,
            'errors': 0
        }
        
        try:
            recent_breaches = DataBreach.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            )
            
            if monitor.keywords:
                recent_breaches = recent_breaches.filter(
                    breach_name__icontains=monitor.keywords[0]
                )
            
            if monitor.industries:
                recent_breaches = recent_breaches.filter(
                    industry__in=monitor.industries
                )
            
            if monitor.countries:
                recent_breaches = recent_breaches.filter(
                    country__in=monitor.countries
                )
            
            summary['checked'] = recent_breaches.count()
            summary['matches'] = recent_breaches.count()
            
            if monitor.alert_on_high_severity:
                high_severity = recent_breaches.filter(severity__in=['high', 'critical'])
                summary['alerts'] = high_severity.count()
            
        except Exception as e:
            logger.error(f"Error monitoring breaches for {organization.name}: {e}")
            summary['errors'] += 1
        
        return summary





