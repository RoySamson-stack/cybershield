"""Services for ransomware monitoring with Tor integration"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from bs4 import BeautifulSoup
from .models import RansomwareGroup, RansomwareIncident, RansomwareMonitor
from apps.core.models import Organization

logger = logging.getLogger(__name__)


class RansomwareService:
    """Service for ransomware monitoring with Tor support"""
    
    def __init__(self, use_tor: bool = False):
        """Initialize ransomware service with optional Tor support"""
        self.use_tor = use_tor or getattr(settings, 'USE_TOR_FOR_RANSOMWARE', False)
        self.session = requests.Session()
        
        if self.use_tor:
            self._setup_tor_proxy()
        else:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
    
    def _setup_tor_proxy(self):
        """Setup Tor SOCKS proxy for .onion site access"""
        try:
            import socks
            import socket
            
            # Default Tor SOCKS proxy (if running locally)
            tor_proxy_host = getattr(settings, 'TOR_PROXY_HOST', '127.0.0.1')
            tor_proxy_port = getattr(settings, 'TOR_PROXY_PORT', 9050)
            
            socks.set_default_proxy(socks.SOCKS5, tor_proxy_host, tor_proxy_port)
            socket.socket = socks.socksocket
            
            self.session.proxies = {
                'http': f'socks5h://{tor_proxy_host}:{tor_proxy_port}',
                'https': f'socks5h://{tor_proxy_host}:{tor_proxy_port}'
            }
            
            logger.info("Tor proxy configured for ransomware monitoring")
        except ImportError:
            logger.warning("PySocks not available, Tor proxy not configured")
            self.use_tor = False
        except Exception as e:
            logger.error(f"Error setting up Tor proxy: {e}")
            self.use_tor = False
    
    def check_onion_site(self, onion_address: str) -> Dict:
        """Check an .onion site for new posts/victims"""
        result = {
            'onion_address': onion_address,
            'is_accessible': False,
            'posts_found': 0,
            'new_posts': 0,
            'error': None
        }
        
        if not onion_address.endswith('.onion'):
            result['error'] = 'Invalid onion address'
            return result
        
        try:
            # Construct .onion URL
            onion_url = f"http://{onion_address}"
            
            # Set longer timeout for Tor connections
            timeout = 30 if self.use_tor else 10
            
            response = self.session.get(onion_url, timeout=timeout, verify=False)
            
            if response.status_code == 200:
                result['is_accessible'] = True
                
                # Parse HTML for victim posts
                soup = BeautifulSoup(response.content, 'html.parser')
                posts = self._extract_victim_posts(soup, onion_address)
                
                result['posts_found'] = len(posts)
                result['new_posts'] = len([p for p in posts if p.get('is_new', False)])
                result['posts'] = posts
            else:
                result['error'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result['error'] = 'Connection timeout'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection failed (Tor may not be running)'
        except Exception as e:
            logger.error(f"Error checking onion site {onion_address}: {e}")
            result['error'] = str(e)
        
        return result
    
    def _extract_victim_posts(self, soup: BeautifulSoup, onion_address: str) -> List[Dict]:
        """Extract victim posts from ransomware site HTML"""
        posts = []
        
        try:
            # Common patterns for ransomware victim listings
            # This is simplified - actual sites have different structures
            
            # Look for common victim post patterns
            # Pattern 1: Table rows with victim data
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        victim_name = cells[0].get_text(strip=True)
                        if victim_name and len(victim_name) > 3:
                            posts.append({
                                'victim_name': victim_name,
                                'date_posted': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                                'description': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                                'onion_address': onion_address,
                                'is_new': True  # Would check against database
                            })
            
            # Pattern 2: List items
            lists = soup.find_all(['ul', 'ol'])
            for list_elem in lists:
                items = list_elem.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if len(text) > 10 and any(keyword in text.lower() for keyword in ['company', 'victim', 'leak', 'data']):
                        posts.append({
                            'victim_name': text[:100],
                            'date_posted': '',
                            'description': text,
                            'onion_address': onion_address,
                            'is_new': True
                        })
            
            # Pattern 3: Divs with specific classes (common in ransomware sites)
            victim_divs = soup.find_all('div', class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['victim', 'post', 'leak', 'company']
            ))
            
            for div in victim_divs:
                text = div.get_text(strip=True)
                if len(text) > 10:
                    posts.append({
                        'victim_name': text[:100],
                        'date_posted': '',
                        'description': text,
                        'onion_address': onion_address,
                        'is_new': True
                    })
                    
        except Exception as e:
            logger.error(f"Error extracting victim posts: {e}")
        
        return posts
    
    def monitor_group_sites(self, group: RansomwareGroup) -> Dict:
        """Monitor all sites for a ransomware group"""
        summary = {
            'group': group.name,
            'sites_checked': 0,
            'sites_accessible': 0,
            'new_incidents': 0,
            'errors': 0
        }
        
        try:
            # Get all active sites for this group
            # This would typically come from RansomwareSite model
            # For now, we'll use group's onion addresses if available
            
            # Placeholder - would integrate with actual site monitoring
            pass
            
        except Exception as e:
            logger.error(f"Error monitoring group {group.name}: {e}")
            summary['errors'] += 1
        
        return summary
    
    def scrape_ransomware_live(self) -> Dict:
        """Scrape ransomware.live for latest groups and sites"""
        summary = {
            'groups_found': 0,
            'sites_found': 0,
            'created': 0,
            'updated': 0,
            'errors': 0
        }
        
        try:
            from apps.monitoring.scrapers import RansomwareLiveScraper
            
            scraper = RansomwareLiveScraper()
            sites = scraper.scrape_all_sites()
            
            summary['sites_found'] = len(sites)
            
            # Process each site
            for site_data in sites:
                try:
                    group_name = site_data.get('group_name', 'Unknown')
                    
                    # Get or create group
                    group, _ = RansomwareGroup.objects.get_or_create(
                        name=group_name,
                        defaults={
                            'display_name': site_data.get('site_name', group_name),
                            'is_active': site_data.get('status') != 'seized',
                            'metadata': {
                                'source': 'ransomware.live',
                                'scraped_at': datetime.now().isoformat()
                            }
                        }
                    )
                    
                    summary['groups_found'] += 1
                    
                    # Create incident record for the site
                    incident, created = RansomwareIncident.objects.update_or_create(
                        group=group,
                        onion_address=site_data.get('onion_address'),
                        defaults={
                            'title': f"{group_name} Site",
                            'description': f"Ransomware site for {group_name}",
                            'onion_address': site_data.get('onion_address'),
                            'clearnet_url': site_data.get('clearnet_url'),
                            'status': 'active' if site_data.get('status') != 'seized' else 'seized',
                            'metadata': site_data.get('metadata', {})
                        }
                    )
                    
                    if created:
                        summary['created'] += 1
                    else:
                        summary['updated'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing site {site_data.get('onion_address')}: {e}")
                    summary['errors'] += 1
                    
        except Exception as e:
            logger.error(f"Error scraping ransomware.live: {e}")
            summary['errors'] += 1
        
        return summary





