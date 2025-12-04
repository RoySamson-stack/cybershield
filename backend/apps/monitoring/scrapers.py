import requests
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RansomwareLiveScraper:
    """Scraper for ransomware.live to extract onion sites"""
    
    BASE_URL = "https://ransomware.live"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_all_groups(self) -> List[Dict]:
        """Get all ransomware groups from ransomware.live"""
        try:
            response = self.session.get(f"{self.BASE_URL}/api/groups", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching groups from ransomware.live: {e}")
            return []
    
    def get_group_details(self, group_name: str) -> Optional[Dict]:
        """Get detailed information about a specific group"""
        try:
            # Try API first
            response = self.session.get(
                f"{self.BASE_URL}/api/groups/{group_name}",
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            
            # Fallback to scraping HTML
            response = self.session.get(
                f"{self.BASE_URL}/groups/{group_name}",
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_group_page(soup, group_name)
        except Exception as e:
            logger.error(f"Error fetching group details for {group_name}: {e}")
            return None
    
    def _parse_group_page(self, soup: BeautifulSoup, group_name: str) -> Dict:
        """Parse HTML page for group information"""
        data = {
            'name': group_name,
            'onion_addresses': [],
            'clearnet_urls': [],
            'status': 'active',
        }
        
        # Look for onion addresses
        text = soup.get_text()
        onion_pattern = r'[a-z0-9]{56}\.onion'
        onion_matches = re.findall(onion_pattern, text, re.IGNORECASE)
        data['onion_addresses'] = list(set(onion_matches))
        
        # Look for links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if '.onion' in href:
                data['onion_addresses'].append(href)
            elif 'http' in href and '.onion' not in href:
                data['clearnet_urls'].append(href)
        
        return data
    
    def scrape_all_sites(self) -> List[Dict]:
        """Scrape all ransomware sites from ransomware.live"""
        sites = []
        
        try:
            groups = self.get_all_groups()
            
            for group in groups:
                group_name = group.get('name', '')
                if not group_name:
                    continue
                
                # Get group details
                details = self.get_group_details(group_name)
                if not details:
                    continue
                
                # Extract onion addresses
                onion_addresses = details.get('onion_addresses', [])
                if not onion_addresses:
                    # Try to get from group data directly
                    onion_addresses = group.get('onion_addresses', [])
                
                # Create site entry for each onion address
                for onion in onion_addresses:
                    sites.append({
                        'group_name': group_name,
                        'onion_address': onion,
                        'clearnet_url': details.get('clearnet_urls', [None])[0],
                        'site_name': group.get('display_name', group_name),
                        'status': group.get('status', 'active'),
                        'source': 'ransomware.live',
                        'source_url': f"{self.BASE_URL}/groups/{group_name}",
                        'metadata': {
                            'group_data': group,
                            'scraped_at': datetime.now().isoformat(),
                        }
                    })
        except Exception as e:
            logger.error(f"Error scraping ransomware.live: {e}")
        
        return sites


class GitHubScraper:
    """Scraper for GitHub repositories to find CVE references"""
    
    GITHUB_API_BASE = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CyberShield-Monitor/1.0'
        }
        if token:
            headers['Authorization'] = f'token {token}'
        self.session.headers.update(headers)
    
    def get_repo_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository information"""
        try:
            response = self.session.get(
                f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching repo info for {owner}/{repo}: {e}")
            return None
    
    def get_latest_commit(self, owner: str, repo: str, branch: str = 'main') -> Optional[Dict]:
        """Get latest commit SHA and date"""
        try:
            response = self.session.get(
                f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/commits/{branch}",
                timeout=30
            )
            response.raise_for_status()
            commit = response.json()
            return {
                'sha': commit['sha'],
                'date': commit['commit']['author']['date'],
                'message': commit['commit']['message'],
            }
        except Exception as e:
            logger.error(f"Error fetching latest commit for {owner}/{repo}: {e}")
            return None
    
    def search_cve_in_repo(self, owner: str, repo: str, since: Optional[str] = None) -> List[Dict]:
        """Search for CVE references in repository commits"""
        cve_refs = []
        cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}', re.IGNORECASE)
        
        try:
            # Get commits
            url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
            params = {'per_page': 100}
            if since:
                params['since'] = since
            
            page = 1
            while True:
                params['page'] = page
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                commits = response.json()
                
                if not commits:
                    break
                
                for commit in commits:
                    # Check commit message
                    message = commit['commit']['message']
                    cve_matches = cve_pattern.findall(message)
                    
                    for cve_id in cve_matches:
                        cve_refs.append({
                            'cve_id': cve_id.upper(),
                            'commit_sha': commit['sha'],
                            'commit_date': commit['commit']['author']['date'],
                            'commit_message': message,
                            'url': commit['html_url'],
                            'file_path': None,  # Would need to check files in commit
                        })
                    
                    # Check commit files if needed
                    # This would require additional API calls
                
                if len(commits) < 100:
                    break
                page += 1
                
        except Exception as e:
            logger.error(f"Error searching CVE in {owner}/{repo}: {e}")
        
        return cve_refs
    
    def get_repo_tree(self, owner: str, repo: str, branch: str = 'main') -> Optional[List[Dict]]:
        """Get repository file tree"""
        try:
            # Get branch SHA
            branch_response = self.session.get(
                f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/branches/{branch}",
                timeout=30
            )
            branch_response.raise_for_status()
            branch_sha = branch_response.json()['commit']['sha']
            
            # Get tree
            tree_response = self.session.get(
                f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{branch_sha}?recursive=1",
                timeout=30
            )
            tree_response.raise_for_status()
            tree = tree_response.json()
            
            return tree.get('tree', [])
        except Exception as e:
            logger.error(f"Error fetching tree for {owner}/{repo}: {e}")
            return None
    
    def find_cve_files(self, owner: str, repo: str) -> List[Dict]:
        """Find files that might contain CVE information"""
        cve_files = []
        cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}', re.IGNORECASE)
        
        try:
            tree = self.get_repo_tree(owner, repo)
            if not tree:
                return []
            
            for item in tree:
                path = item.get('path', '')
                # Look for CVE in path or common exploit file patterns
                if (cve_pattern.search(path) or 
                    any(keyword in path.lower() for keyword in ['exploit', 'poc', 'cve', 'vuln'])):
                    cve_files.append({
                        'path': path,
                        'sha': item.get('sha'),
                        'type': item.get('type'),
                        'url': f"https://github.com/{owner}/{repo}/blob/main/{path}",
                    })
        except Exception as e:
            logger.error(f"Error finding CVE files in {owner}/{repo}: {e}")
        
        return cve_files

