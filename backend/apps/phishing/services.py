"""Services for phishing detection and domain reputation checking"""
import requests
import logging
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .models import PhishingCampaign, PhishingDomain, PhishingMonitor
from apps.core.models import Organization

logger = logging.getLogger(__name__)


class PhishingService:
    """Service for phishing detection and domain monitoring"""
    
    def __init__(self):
        """Initialize phishing service"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CyberShield/1.0'
        })
    
    def check_domain_reputation(self, domain: str) -> Dict:
        """Check domain reputation using multiple sources"""
        reputation = {
            'domain': domain,
            'is_suspicious': False,
            'is_phishing': False,
            'reputation_score': 50,  # Neutral
            'sources': [],
            'details': {}
        }
        
        try:
            domain_age = self._check_domain_age(domain)
            if domain_age:
                reputation['details']['domain_age_days'] = domain_age
                if domain_age < 30:
                    reputation['is_suspicious'] = True
                    reputation['reputation_score'] -= 20
            
            similarity_score = self._check_domain_similarity(domain)
            if similarity_score:
                reputation['details']['similarity_score'] = similarity_score
                if similarity_score > 0.8:
                    reputation['is_suspicious'] = True
                    reputation['reputation_score'] -= 15
            
            ssl_info = self._check_ssl_certificate(domain)
            if ssl_info:
                reputation['details']['ssl'] = ssl_info
                if not ssl_info.get('has_ssl'):
                    reputation['is_suspicious'] = True
                    reputation['reputation_score'] -= 10
            
            whois_info = self._check_whois(domain)
            if whois_info:
                reputation['details']['whois'] = whois_info
                if whois_info.get('is_private'):
                    reputation['reputation_score'] -= 5
            
            dns_info = self._check_dns_records(domain)
            if dns_info:
                reputation['details']['dns'] = dns_info
            
            reputation['reputation_score'] = max(0, min(100, reputation['reputation_score']))
            
            if reputation['reputation_score'] < 40:
                reputation['is_phishing'] = True
            
        except Exception as e:
            logger.error(f"Error checking domain reputation for {domain}: {e}")
        
        return reputation
    
    def _check_domain_age(self, domain: str) -> Optional[int]:
        """Check domain age in days"""
        try:
            import whois
            domain_info = whois.whois(domain)
            
            if domain_info.creation_date:
                if isinstance(domain_info.creation_date, list):
                    creation_date = domain_info.creation_date[0]
                else:
                    creation_date = domain_info.creation_date
                
                if isinstance(creation_date, datetime):
                    age_days = (timezone.now() - timezone.make_aware(creation_date)).days
                    return age_days
        except ImportError:
            logger.warning("python-whois not available for domain age check")
        except Exception as e:
            logger.debug(f"Could not check domain age for {domain}: {e}")
        
        return None
    
    def _check_domain_similarity(self, domain: str) -> Optional[float]:
        """Check domain similarity to known brands (simplified)"""
        known_brands = [
            'google', 'facebook', 'microsoft', 'amazon', 'apple',
            'paypal', 'ebay', 'twitter', 'linkedin', 'github',
            'netflix', 'spotify', 'dropbox', 'adobe', 'oracle'
        ]
        
        domain_lower = domain.lower().replace('www.', '').split('.')[0]
        
        max_similarity = 0.0
        for brand in known_brands:
            similarity = self._calculate_similarity(domain_lower, brand)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity if max_similarity > 0.7 else None
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple similarity score between two strings"""
        if not s1 or not s2:
            return 0.0
        
        set1 = set(s1.lower())
        set2 = set(s2.lower())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _check_ssl_certificate(self, domain: str) -> Optional[Dict]:
        """Check SSL certificate information"""
        try:
            import ssl
            import socket
            
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        'has_ssl': True,
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'not_after': cert.get('notAfter', ''),
                    }
        except Exception as e:
            logger.debug(f"SSL check failed for {domain}: {e}")
            return {'has_ssl': False, 'error': str(e)}
    
    def _check_whois(self, domain: str) -> Optional[Dict]:
        """Check WHOIS information"""
        try:
            import whois
            domain_info = whois.whois(domain)
            
            return {
                'registrar': domain_info.registrar if hasattr(domain_info, 'registrar') else None,
                'creation_date': str(domain_info.creation_date) if hasattr(domain_info, 'creation_date') else None,
                'expiration_date': str(domain_info.expiration_date) if hasattr(domain_info, 'expiration_date') else None,
                'is_private': domain_info.private if hasattr(domain_info, 'private') else False,
            }
        except ImportError:
            logger.warning("python-whois not available")
        except Exception as e:
            logger.debug(f"WHOIS check failed for {domain}: {e}")
        
        return None
    
    def _check_dns_records(self, domain: str) -> Optional[Dict]:
        """Check DNS records"""
        try:
            import dns.resolver
            
            dns_info = {
                'a_records': [],
                'mx_records': [],
            'txt_records': [],
        }
            
            try:
                answers = dns.resolver.resolve(domain, 'A')
                dns_info['a_records'] = [str(rdata) for rdata in answers]
            except:
                pass
            
            try:
                answers = dns.resolver.resolve(domain, 'MX')
                dns_info['mx_records'] = [str(rdata) for rdata in answers]
            except:
                pass
            
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                dns_info['txt_records'] = [str(rdata) for rdata in answers]
            except:
                pass
            
            return dns_info
        except ImportError:
            logger.warning("dnspython not available for DNS checks")
        except Exception as e:
            logger.debug(f"DNS check failed for {domain}: {e}")
        
        return None
    
    def scan_domain(self, domain: str, target_brand: Optional[str] = None) -> Dict:
        """Complete domain scan for phishing detection"""
        result = {
            'domain': domain,
            'is_phishing': False,
            'threat_level': 'low',
            'reputation': None,
            'recommendations': []
        }
        
        reputation = self.check_domain_reputation(domain)
        result['reputation'] = reputation
        
        if reputation['is_phishing']:
            result['is_phishing'] = True
            result['threat_level'] = 'critical'
        elif reputation['is_suspicious']:
            result['threat_level'] = 'high'
        elif reputation['reputation_score'] < 60:
            result['threat_level'] = 'medium'
        
        if not reputation['details'].get('ssl', {}).get('has_ssl'):
            result['recommendations'].append('Domain lacks SSL certificate')
        
        if reputation['details'].get('domain_age_days', 999) < 30:
            result['recommendations'].append('Domain is very new (potential typosquatting)')
        
        if reputation['details'].get('similarity_score', 0) > 0.8:
            result['recommendations'].append('Domain name is suspiciously similar to known brand')
        
        return result
    
    def monitor_domains(self, monitor: PhishingMonitor) -> Dict:
        """Monitor domains based on monitor configuration"""
        summary = {
            'scanned': 0,
            'phishing_detected': 0,
            'suspicious': 0,
            'created': 0,
            'errors': 0
        }
        
        try:
            pass
            
        except Exception as e:
            logger.error(f"Error monitoring phishing domains: {e}")
            summary['errors'] += 1
        
        return summary





