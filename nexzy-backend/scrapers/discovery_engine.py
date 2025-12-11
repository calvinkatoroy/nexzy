"""
Discovery Engine for Nexzy - Project NEXT Intelligence
Automated OSINT scraper for detecting leaked credentials on paste sites

This module:
- Scrapes paste sites (Pastebin, Paste.ee, etc.)
- Extracts emails and credentials
- Calculates relevance scores based on target domain
- Optionally crawls author profiles
- Provides structured results for database storage

Adapted from the original project_discovery module
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import re
import random
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from datetime import datetime
import sys
import os

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import (
        TARGET_DOMAIN, REQUEST_DELAY, MAX_RETRIES,
        MIN_RELEVANCE_SCORE, LEAK_KEYWORDS, USER_AGENTS,
        CLEARNET_SOURCES
    )
except ImportError:
    # Fallback defaults if config not available
    TARGET_DOMAIN = "ui.ac.id"
    REQUEST_DELAY = 2
    MAX_RETRIES = 3
    MIN_RELEVANCE_SCORE = 0.3
    LEAK_KEYWORDS = ["password", "credentials", "leaked", "database", "dump", "breach"]
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    ]
    CLEARNET_SOURCES = ["https://pastebin.com"]

# Setup logging
logger = logging.getLogger(__name__)


class DiscoveryOrchestrator:
    """
    Main orchestrator for clearnet discovery with relevance scoring.
    Analyzes paste sites for leaked credentials related to target domain.
    """
    
    def __init__(self):
        """Initialize the discovery orchestrator"""
        self.session = requests.Session()
        self.discovered_urls = set()
        self.processed_authors = set()
        
    def _get_random_user_agent(self) -> str:
        """Return a random user agent string to avoid detection"""
        return random.choice(USER_AGENTS)
    
    def _make_request(self, url: str, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic and rate limiting.
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
            
        Returns:
            Response object or None if failed
        """
        for attempt in range(retries):
            try:
                headers = {
                    'User-Agent': self._get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                }
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=15,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    # Rate limiting
                    time.sleep(REQUEST_DELAY)
                    return response
                elif response.status_code == 404:
                    logger.warning(f"URL not found: {url}")
                    return None
                elif response.status_code == 429:
                    logger.warning(f"Rate limited on {url}, waiting...")
                    time.sleep(REQUEST_DELAY * 3)
                else:
                    logger.warning(f"Status {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(REQUEST_DELAY * 2)
        
        return None
    
    def _calculate_relevance_score(self, text: str, title: str = "") -> float:
        """
        Calculate relevance score based on:
        - Target domain mentions
        - Email presence (any domain)
        - Leak keywords
        - PII detection (NPM, phone, addresses)
        
        Scoring (more sensitive):
        - 30% for domain mentions
        - 30% for any emails found
        - 20% for leak keywords
        - 20% for PII patterns
        
        Args:
            text: Content to analyze
            title: Optional title text
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        text_lower = text.lower()
        combined = f"{title} {text}".lower()
        
        # Check domain mentions (30 points)
        domain_count = combined.count(TARGET_DOMAIN.lower())
        if domain_count > 0:
            score += min(domain_count * 0.15, 0.3)
        
        # Check for ANY emails (30 points) - lebih sensitif
        all_emails = self._extract_emails(text)
        if len(all_emails) > 0:
            score += min(len(all_emails) * 0.05, 0.3)
        
        # Check for target domain emails (bonus 20 points)
        target_emails = self._extract_target_domain_emails(text)
        if len(target_emails) > 0:
            score += min(len(target_emails) * 0.1, 0.2)
        
        # Check for leak keywords (20 points)
        keyword_matches = sum(1 for keyword in LEAK_KEYWORDS if keyword in text_lower)
        if keyword_matches > 0:
            score += min(keyword_matches * 0.04, 0.2)
        
        # Check for PII patterns (20 points) - NPM, phone, addresses
        pii_score = 0.0
        # NPM pattern (Indonesian student ID)
        if re.search(r'\b\d{10}\b', text):  # 10 digit NPM
            pii_score += 0.1
        # Indonesian phone numbers
        if re.search(r'\+?62\s?\d{2,3}[\s-]?\d{3,4}[\s-]?\d{3,4}', text):
            pii_score += 0.05
        if re.search(r'0\d{2,3}[\s-]?\d{3,4}[\s-]?\d{3,4}', text):
            pii_score += 0.05
        # Address patterns
        if re.search(r'(jalan|jl\.|alamat|address|kota|kelurahan)', text_lower):
            pii_score += 0.05
        
        score += min(pii_score, 0.2)
        
        return min(score, 1.0)
    
    def _extract_emails(self, text: str) -> Set[str]:
        """
        Extract all email addresses from text.
        
        Args:
            text: Text to search
            
        Returns:
            Set of email addresses
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return set(emails)
    
    def _extract_target_domain_emails(self, text: str) -> Set[str]:
        """
        Extract email addresses specifically from the target domain.
        
        Args:
            text: Text to search
            
        Returns:
            Set of target domain email addresses
        """
        all_emails = self._extract_emails(text)
        target_emails = {
            email for email in all_emails 
            if TARGET_DOMAIN.lower() in email.lower()
        }
        return target_emails
    
    def _contains_credentials(self, text: str) -> bool:
        """
        Check if text contains sensitive data: credentials, PII, or leaked personal information.
        
        Detects:
        - Traditional credentials (email:password)
        - Indonesian student data (NPM, phone numbers, addresses)
        - Personal information leaks (names, addresses, phone numbers)
        - Database dumps
        
        Args:
            text: Text to check
            
        Returns:
            True if sensitive data detected
        """
        # Traditional credential patterns
        credential_patterns = [
            r'\b\w+:\w+@',  # user:pass@
            r'\b\w+:\w{6,}\b',  # user:password (6+ chars)
            r'password\s*[:=]\s*\S+',  # password: xxx or password=xxx
            r'username\s*[:=]\s*\S+.*password\s*[:=]\s*\S+',  # username/password pair
        ]
        
        # PII (Personal Identifiable Information) patterns - Indonesian context
        pii_patterns = [
            r'npm\s*[:=]\s*\d{10}',  # NPM: 2006596371
            r'no\.?\s*hp\s*(pribadi|orang\s*tua)?\s*[:=]\s*[\d\s\+\-\(\)]{8,}',  # Phone: 87781835703
            r'nik\s*[:=]\s*\d{16}',  # NIK (Indonesian ID)
            r'alamat\s*(rumah|kost|lengkap)?\s*[:=]',  # Address patterns
            r'tempat\s*lahir\s*[:=]',  # Birth place
            r'tanggal\s*lahir\s*[:=]',  # Birth date
            r'nama\s*(lengkap|panggilan)\s*[:=]',  # Full name patterns
            r'program\s*studi\s*[:=]',  # Study program
            r'jalur\s*masuk\s*[:=]',  # University entry method
            r'fakultas\s*[:=]',  # Faculty
        ]
        
        # Database leak indicators
        leak_indicators = [
            r'database\s+(dump|leak|breach)',
            r'leaked\s+(credentials|data|database)',
            r'(dump|leaked)\s+\d+\s+(users|accounts|emails)',
        ]
        
        text_lower = text.lower()
        
        # Check for traditional credentials
        for pattern in credential_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check for PII patterns (Indonesian student data leaks)
        for pattern in pii_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.info(f"[PII] Pattern detected: {pattern}")
                return True
        
        # Check for database leak indicators
        for pattern in leak_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check if contains multiple personal data fields (heuristic)
        # If we find 3+ of these keywords, it's likely a data leak
        pii_keywords = ['nama', 'npm', 'email', 'alamat', 'no. hp', 'hp pribadi', 
                        'tanggal lahir', 'tempat lahir', 'fakultas', 'jurusan']
        keyword_count = sum(1 for keyword in pii_keywords if keyword in text_lower)
        
        if keyword_count >= 3:
            logger.info(f"[ALERT] Multiple PII fields detected ({keyword_count} fields)")
            return True
        
        return False
    
    def _get_raw_url(self, paste_url: str) -> Optional[str]:
        """
        Convert paste URL to raw content URL.
        
        Args:
            paste_url: Regular paste URL
            
        Returns:
            Raw content URL or None
        """
        if 'pastebin.com' in paste_url:
            paste_id = paste_url.split('/')[-1]
            return f"https://pastebin.com/raw/{paste_id}"
        elif 'paste.ee' in paste_url:
            paste_id = paste_url.split('/')[-1]
            return f"https://paste.ee/r/{paste_id}"
        else:
            return paste_url
    
    def _extract_paste_metadata(self, paste_url: str) -> Dict:
        """
        Extract metadata from paste page (author, title, date).
        
        Args:
            paste_url: URL of the paste
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            'author': 'unknown',
            'title': '',
            'date': ''
        }
        
        try:
            response = self._make_request(paste_url)
            if not response:
                return metadata
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Pastebin-specific extraction
            if 'pastebin.com' in paste_url:
                author_elem = soup.find('div', class_='username')
                if author_elem:
                    author_link = author_elem.find('a')
                    if author_link:
                        metadata['author'] = author_link.text.strip()
                
                title_elem = soup.find('div', class_='paste_box_line1')
                if title_elem:
                    metadata['title'] = title_elem.get_text(strip=True)
            
            # Generic fallback
            if metadata['author'] == 'unknown':
                author_meta = soup.find('meta', {'name': 'author'})
                if author_meta:
                    metadata['author'] = author_meta.get('content', 'unknown')
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from {paste_url}: {e}")
        
        return metadata
    
    def analyze_paste(self, paste_url: str) -> Optional[Dict]:
        """
        Analyze a single paste URL for relevant content.
        
        Args:
            paste_url: URL to analyze
            
        Returns:
            Dictionary with analysis results or None if irrelevant
        """
        logger.info(f"Analyzing: {paste_url}")
        
        # Get raw content
        raw_url = self._get_raw_url(paste_url)
        if not raw_url:
            return None
        
        response = self._make_request(raw_url)
        if not response:
            return None
        
        content = response.text
        
        # Extract metadata
        metadata = self._extract_paste_metadata(paste_url)
        
        # Calculate relevance
        relevance_score = self._calculate_relevance_score(
            content, 
            metadata.get('title', '')
        )
        
        # Check for credentials FIRST - if has credentials, always include
        has_credentials = self._contains_credentials(content)
        
        # Skip only if NO credentials AND low relevance
        if not has_credentials and relevance_score < MIN_RELEVANCE_SCORE:
            logger.info(f"No credentials and low relevance ({relevance_score:.2f}), skipping")
            return None
        
        # Extract emails
        all_emails = self._extract_emails(content)
        target_emails = self._extract_target_domain_emails(content)
        
        result = {
            'url': paste_url,
            'source': urlparse(paste_url).netloc,
            'author': metadata.get('author', 'unknown'),
            'title': metadata.get('title', ''),
            'relevance_score': relevance_score,
            'emails': list(all_emails),
            'target_emails': list(target_emails),
            'has_credentials': has_credentials,
            'discovered_at': datetime.utcnow().isoformat(),
            # Provide content preview for AI module input
            'content_preview': content[:2000]
        }
        
        logger.info(
            f"[FOUND] Relevant paste! "
            f"Score: {relevance_score:.2f}, "
            f"Emails: {len(all_emails)}, "
            f"Target: {len(target_emails)}"
        )
        
        return result
    
    def crawl_user_pastes(
        self, 
        username: str, 
        base_url: str = "https://pastebin.com"
    ) -> List[Dict]:
        """
        Crawl all pastes from a specific user's profile.
        
        Args:
            username: Username to crawl
            base_url: Base URL of the paste site
            
        Returns:
            List of discovered paste results
        """
        if username in self.processed_authors or username == 'unknown':
            return []
        
        self.processed_authors.add(username)
        logger.info(f"[CRAWL] Crawling author profile: {username}")
        
        results = []
        
        try:
            # Pastebin user profile
            if 'pastebin.com' in base_url:
                user_url = f"{base_url}/u/{username}"
                response = self._make_request(user_url)
                
                if not response:
                    logger.warning(f"[WARNING] Could not access profile: {username}")
                    return results
                
                soup = BeautifulSoup(response.text, 'html.parser')
                paste_links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z0-9]{8}$'))
                
                logger.info(f"[INFO] Found {len(paste_links)} pastes from {username}, analyzing top 20...")
                
                for idx, link in enumerate(paste_links[:20], 1):  # Increased to 20 pastes per author
                    paste_url = f"{base_url}{link['href']}"
                    
                    if paste_url not in self.discovered_urls:
                        self.discovered_urls.add(paste_url)
                        logger.info(f"  [{idx}/20] Analyzing: {paste_url}")
                        result = self.analyze_paste(paste_url)
                        if result:
                            results.append(result)
                            cred_status = "[CREDENTIALS]" if result['has_credentials'] else "[NO CREDS]"
                            logger.info(f"    {cred_status} Relevance: {result['relevance_score']:.2f}, Emails: {len(result['emails'])}")
                
                logger.info(f"[COMPLETE] Author crawl complete: {len(results)} sensitive pastes found")
        
        except Exception as e:
            logger.error(f"Failed to crawl user {username}: {e}")
        
        return results
    
    def run_full_discovery(
        self,
        clearnet_urls: List[str] = None,
        enable_clearnet: bool = True,
        enable_darknet: bool = False,
        crawl_authors: bool = True
    ) -> Dict:
        """
        Run complete discovery across provided URLs.
        
        Args:
            clearnet_urls: Initial list of paste URLs to analyze
            enable_clearnet: Whether to enable clearnet discovery
            enable_darknet: Whether to enable darknet (not implemented)
            crawl_authors: Whether to crawl paste authors' profiles
            
        Returns:
            Dictionary with all results and metadata
        """
        logger.info("=" * 70)
        logger.info("NEXZY DISCOVERY ENGINE - STARTING SCAN")
        logger.info(f"Target Domain: {TARGET_DOMAIN}")
        logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"URLs to scan: {len(clearnet_urls) if clearnet_urls else 0}")
        logger.info("=" * 70)
        
        all_results = []
        
        if not enable_clearnet or not clearnet_urls:
            logger.warning("No URLs provided or clearnet disabled")
            return {
                'discovered_items': all_results,
                'total_found': 0,
                'scan_time': datetime.utcnow().isoformat()
            }
        
        # Process initial URLs
        for url in clearnet_urls:
            try:
                result = self.analyze_paste(url)
                if result:
                    all_results.append(result)
                    
                    # Optionally crawl author's other pastes
                    if crawl_authors and result['author'] != 'unknown':
                        author_results = self.crawl_user_pastes(
                            result['author'],
                            f"https://{result['source']}"
                        )
                        all_results.extend(author_results)
                        
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info("=" * 70)
        logger.info(f"DISCOVERY COMPLETE - Found {len(all_results)} relevant items")
        logger.info("=" * 70)
        
        return {
            'discovered_items': all_results,
            'total_found': len(all_results),
            'target_domain': TARGET_DOMAIN,
            'scan_time': datetime.utcnow().isoformat(),
            'urls_scanned': len(clearnet_urls)
        }


# ==============================================================================
# STANDALONE TESTING
# ==============================================================================

if __name__ == "__main__":
    # Example usage
    orchestrator = DiscoveryOrchestrator()
    
    test_urls = [
        "https://pastebin.com/raw/test123",
    ]
    
    results = orchestrator.run_full_discovery(
        clearnet_urls=test_urls,
        enable_clearnet=True,
        crawl_authors=False
    )
    
    print(f"\nFound {results['total_found']} results")
    for item in results['discovered_items']:
        print(f"  - {item['url']} (Score: {item['relevance_score']:.2f})")
