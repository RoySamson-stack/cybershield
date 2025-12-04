"""Services for security scanning"""
import requests
import socket
import ssl
import subprocess
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from django.utils import timezone
from django.conf import settings
from .models import ScanTarget, SecurityScan, Vulnerability
from apps.core.services import BillingService
from apps.core.models import Organization
from apps.cve.models import CVE

logger = __import__('logging').getLogger(__name__)


class ScannerService:
    """Service for performing security scans"""
    
    @staticmethod
    def create_scan(organization, target_id, scan_type='full'):
        """Create and initiate a security scan"""
        try:
            target = ScanTarget.objects.get(id=target_id, organization=organization)
        except ScanTarget.DoesNotExist:
            return {'success': False, 'error': 'Scan target not found'}
        
        # Check usage limit
        billing_check = BillingService.check_and_track_usage(
            organization, 'scan', count=1
        )
        
        if not billing_check['allowed']:
            return billing_check
        
        # Create scan record
        scan = SecurityScan.objects.create(
            organization=organization,
            target=target,
            scan_type=scan_type,
            status='pending',
            started_at=timezone.now()
        )
        
        # In production, this would queue a Celery task
        # For now, perform basic scan
        ScannerService._perform_scan(scan)
        
        return {
            'success': True,
            'scan_id': str(scan.id),
            'status': scan.status,
            'usage': billing_check
        }
    
    @staticmethod
    def _perform_scan(scan):
        """Perform the actual scan (enhanced implementation)"""
        scan.status = 'running'
        scan.save()
        
        target_value = scan.target.target_value
        vulnerabilities = []
        
        try:
            if scan.scan_type in ['ssl', 'full']:
                # SSL/TLS scan
                ssl_results = ScannerService._scan_ssl(target_value)
                if ssl_results:
                    vulnerabilities.extend(ssl_results)
            
            if scan.scan_type in ['port', 'full']:
                # Port scan with Nmap
                port_results = ScannerService._scan_ports_nmap(target_value)
                if port_results:
                    vulnerabilities.extend(port_results)
            
            if scan.scan_type in ['web', 'full']:
                # Web scan
                web_results = ScannerService._scan_web(target_value)
                if web_results:
                    vulnerabilities.extend(web_results)
            
            if scan.scan_type in ['vulnerability', 'full']:
                # Vulnerability scan with CVE matching
                vuln_results = ScannerService._scan_vulnerabilities(target_value, vulnerabilities)
                if vuln_results:
                    vulnerabilities.extend(vuln_results)
            
            # Calculate risk score
            risk_score = ScannerService._calculate_risk_score(vulnerabilities)
            
            # Update scan
            scan.status = 'completed'
            scan.completed_at = timezone.now()
            scan.duration_seconds = (scan.completed_at - scan.started_at).total_seconds()
            scan.risk_score = risk_score
            scan.vulnerabilities_found = len(vulnerabilities)
            scan.vulnerabilities_critical = len([v for v in vulnerabilities if v.get('severity') == 'critical'])
            scan.vulnerabilities_high = len([v for v in vulnerabilities if v.get('severity') == 'high'])
            scan.vulnerabilities_medium = len([v for v in vulnerabilities if v.get('severity') == 'medium'])
            scan.vulnerabilities_low = len([v for v in vulnerabilities if v.get('severity') == 'low'])
            scan.results = {
                'vulnerabilities': vulnerabilities,
                'summary': {
                    'total': len(vulnerabilities),
                    'by_severity': {
                        'critical': scan.vulnerabilities_critical,
                        'high': scan.vulnerabilities_high,
                        'medium': scan.vulnerabilities_medium,
                        'low': scan.vulnerabilities_low,
                    }
                }
            }
            scan.save()
            
            # Create vulnerability records
            for vuln_data in vulnerabilities:
                Vulnerability.objects.create(
                    scan=scan,
                    title=vuln_data.get('title', 'Unknown'),
                    description=vuln_data.get('description', ''),
                    severity=vuln_data.get('severity', 'low'),
                    cvss_score=vuln_data.get('cvss_score'),
                    cve_id=vuln_data.get('cve_id'),
                    affected_component=vuln_data.get('component'),
                    recommendation=vuln_data.get('recommendation'),
                    references=vuln_data.get('references', []),
                )
            
        except Exception as e:
            logger.error(f"Error performing scan {scan.id}: {e}")
            scan.status = 'failed'
            scan.error_message = str(e)
            scan.save()
    
    @staticmethod
    def _scan_ssl(domain):
        """Scan SSL/TLS configuration"""
        vulnerabilities = []
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    # Check certificate expiration
                    import datetime
                    not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.datetime.now()).days
                    
                    if days_until_expiry < 30:
                        vulnerabilities.append({
                            'title': 'SSL Certificate Expiring Soon',
                            'description': f'Certificate expires in {days_until_expiry} days',
                            'severity': 'medium' if days_until_expiry < 7 else 'low',
                            'component': 'SSL Certificate',
                            'recommendation': 'Renew SSL certificate before expiration'
                        })
                    
                    # Check TLS version
                    if cipher and cipher[1]:
                        if 'TLSv1.0' in cipher[1] or 'TLSv1.1' in cipher[1]:
                            vulnerabilities.append({
                                'title': 'Weak TLS Version',
                                'description': f'Using deprecated TLS version: {cipher[1]}',
                                'severity': 'high',
                                'component': 'TLS Protocol',
                                'recommendation': 'Upgrade to TLS 1.2 or higher'
                            })
                    
                    # Check certificate chain
                    if not cert.get('issuer'):
                        vulnerabilities.append({
                            'title': 'SSL Certificate Chain Issue',
                            'description': 'Certificate chain may be incomplete',
                            'severity': 'medium',
                            'component': 'SSL Certificate',
                            'recommendation': 'Ensure complete certificate chain is configured'
                        })
        except ssl.SSLError as e:
            vulnerabilities.append({
                'title': 'SSL/TLS Configuration Error',
                'description': f'SSL error: {str(e)}',
                'severity': 'high',
                'component': 'SSL/TLS',
                'recommendation': 'Check SSL certificate configuration'
            })
        except Exception as e:
            vulnerabilities.append({
                'title': 'SSL/TLS Connection Failed',
                'description': f'Could not establish SSL connection: {str(e)}',
                'severity': 'high',
                'component': 'SSL/TLS',
                'recommendation': 'Check SSL certificate configuration'
            })
        
        return vulnerabilities
    
    @staticmethod
    def _scan_ports_nmap(host):
        """Advanced port scan using Nmap"""
        vulnerabilities = []
        open_ports = []
        
        try:
            import nmap
            nm = nmap.PortScanner()
            
            # Perform a quick scan of common ports
            nm.scan(host, '21-443,3306,5432,8080,8443', arguments='-sV --version-intensity 2')
            
            for hostname in nm.all_hosts():
                for proto in nm[hostname].all_protocols():
                    ports = nm[hostname][proto].keys()
                    for port in ports:
                        port_info = nm[hostname][proto][port]
                        if port_info['state'] == 'open':
                            open_ports.append({
                                'port': port,
                                'service': port_info.get('name', 'unknown'),
                                'version': port_info.get('version', ''),
                                'product': port_info.get('product', ''),
                            })
            
            # Check for risky open ports
            risky_ports = {
                21: 'FTP',
                23: 'Telnet',
                1433: 'MSSQL',
                3306: 'MySQL',
                5432: 'PostgreSQL',
                3389: 'RDP',
            }
            
            for port_data in open_ports:
                port_num = port_data['port']
                if port_num in risky_ports:
                    vulnerabilities.append({
                        'title': f'Risky Service Exposed: {risky_ports[port_num]}',
                        'description': f'Port {port_num} ({risky_ports[port_num]}) is open and accessible',
                        'severity': 'high',
                        'component': f'Port {port_num}',
                        'recommendation': f'Restrict access to {risky_ports[port_num]} or use VPN'
                    })
            
            if open_ports:
                vulnerabilities.append({
                    'title': 'Open Ports Detected',
                    'description': f'Found {len(open_ports)} open ports',
                    'severity': 'medium',
                    'component': 'Network',
                    'recommendation': 'Review and close unnecessary open ports',
                    'references': [{'type': 'ports', 'data': open_ports}]
                })
        except ImportError:
            # Fallback to basic port scan if nmap not available
            logger.warning("python-nmap not available, using basic port scan")
            return ScannerService._scan_ports(host)
        except Exception as e:
            logger.error(f"Error in Nmap scan: {e}")
            # Fallback to basic scan
            return ScannerService._scan_ports(host)
        
        return vulnerabilities
    
    @staticmethod
    def _scan_ports(host):
        """Basic port scan fallback"""
        vulnerabilities = []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 5432, 8080]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
        
        if open_ports:
            vulnerabilities.append({
                'title': 'Open Ports Detected',
                'description': f'Found {len(open_ports)} open ports: {open_ports}',
                'severity': 'medium',
                'component': 'Network',
                'recommendation': 'Review and close unnecessary open ports'
            })
        
        return vulnerabilities
    
    @staticmethod
    def _scan_web(url):
        """Enhanced web application scan"""
        vulnerabilities = []
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            response = requests.get(url, timeout=10, verify=False, allow_redirects=True)
            
            # Check security headers
            security_headers = {
                'X-Frame-Options': 'medium',
                'X-Content-Type-Options': 'medium',
                'Strict-Transport-Security': 'high',
                'Content-Security-Policy': 'high',
                'X-XSS-Protection': 'low',
            }
            
            missing_headers = []
            for header, severity in security_headers.items():
                if header not in response.headers:
                    missing_headers.append({
                        'header': header,
                        'severity': severity
                    })
            
            if missing_headers:
                high_severity = [h for h in missing_headers if h['severity'] == 'high']
                max_severity = 'high' if high_severity else 'medium'
                
                vulnerabilities.append({
                    'title': 'Missing Security Headers',
                    'description': f'Missing security headers: {", ".join([h["header"] for h in missing_headers])}',
                    'severity': max_severity,
                    'component': 'HTTP Headers',
                    'recommendation': 'Add security headers to improve application security',
                    'references': [{'type': 'headers', 'data': missing_headers}]
                })
            
            # Check for server information disclosure
            server_header = response.headers.get('Server', '')
            if server_header:
                vulnerabilities.append({
                    'title': 'Server Information Disclosure',
                    'description': f'Server header reveals: {server_header}',
                    'severity': 'low',
                    'component': 'HTTP Headers',
                    'recommendation': 'Consider hiding or modifying server header'
                })
            
            # Check HTTP vs HTTPS redirect
            if url.startswith('http://') and response.url.startswith('https://'):
                vulnerabilities.append({
                    'title': 'HTTP to HTTPS Redirect',
                    'description': 'HTTP redirects to HTTPS (good practice)',
                    'severity': 'info',
                    'component': 'HTTP Protocol',
                    'recommendation': 'Consider enforcing HTTPS only'
                })
            
        except requests.exceptions.SSLError:
            vulnerabilities.append({
                'title': 'SSL Certificate Error',
                'description': 'SSL certificate validation failed',
                'severity': 'high',
                'component': 'SSL/TLS',
                'recommendation': 'Fix SSL certificate issues'
            })
        except Exception as e:
            vulnerabilities.append({
                'title': 'Web Scan Failed',
                'description': f'Could not scan web application: {str(e)}',
                'severity': 'low',
                'component': 'Web Application',
            })
        
        return vulnerabilities
    
    @staticmethod
    def _scan_vulnerabilities(target_value, existing_vulns):
        """Match vulnerabilities with CVE database"""
        vulnerabilities = []
        
        try:
            # Extract service/software information from existing vulnerabilities
            services = []
            for vuln in existing_vulns:
                component = vuln.get('component', '')
                if component and component not in services:
                    services.append(component)
            
            # Search CVE database for related vulnerabilities
            # This is a simplified version - in production, you'd match against
            # actual software versions detected during scanning
            if services:
                # Search for recent high-severity CVEs
                recent_cves = CVE.objects.filter(
                    cvss_score__gte=7.0
                ).order_by('-published_date')[:10]
                
                for cve in recent_cves:
                    # Simple keyword matching (in production, use proper CPE matching)
                    cve_description = cve.description.lower()
                    for service in services:
                        if service.lower() in cve_description:
                            vulnerabilities.append({
                                'title': f'Potential CVE Match: {cve.cve_id}',
                                'description': cve.description[:200],
                                'severity': 'high' if cve.cvss_score >= 7.0 else 'medium',
                                'cvss_score': float(cve.cvss_score),
                                'cve_id': cve.cve_id,
                                'component': service,
                                'recommendation': f'Review and patch {cve.cve_id}',
                                'references': [{'type': 'cve', 'url': cve.references[0] if cve.references else ''}]
                            })
                            break
        except Exception as e:
            logger.error(f"Error in vulnerability scan: {e}")
        
        return vulnerabilities
    
    @staticmethod
    def _calculate_risk_score(vulnerabilities):
        """Calculate overall risk score (0-100)"""
        if not vulnerabilities:
            return 0
        
        severity_scores = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3,
            'info': 1
        }
        
        total_score = sum(severity_scores.get(v.get('severity', 'low'), 0) for v in vulnerabilities)
        return min(100, total_score)
