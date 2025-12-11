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
        CLEARNET_SOURCES, DARKWEB_SOURCES, TOR_PROXY_ENABLED, TOR_PROXY_URL
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
    DARKWEB_SOURCES = []
    TOR_PROXY_ENABLED = False
    TOR_PROXY_URL = None

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
        
        # Setup Tor proxy if enabled
        if TOR_PROXY_ENABLED and TOR_PROXY_URL:
            self.tor_session = requests.Session()
            self.tor_session.proxies = {
                'http': TOR_PROXY_URL,
                'https': TOR_PROXY_URL
            }
            logger.info(f"Tor proxy enabled: {TOR_PROXY_URL}")
        else:
            self.tor_session = None
    
    def search_pastebin_by_keyword(self, keyword: str, limit: int = 50) -> List[str]:
        """
        Search Pastebin using their search functionality.
        Scrapes search results for pastes containing the keyword.
        
        Args:
            keyword: Search keyword (e.g., "ui.ac.id", "universitas indonesia")
            limit: Maximum number of URLs to return
            
        Returns:
            List of paste URLs from search results
        """
        discovered_urls = []
        
        try:
            # Method 1: Use Pastebin search (searches public pastes)
            logger.info(f"[PASTEBIN SEARCH] Searching for: {keyword}")
            search_url = f"https://pastebin.com/search?q={keyword}"
            
            response = self._make_request(search_url)
            if not response:
                logger.warning("[PASTEBIN SEARCH] Failed to fetch search page")
                return self._fallback_archive_search(keyword, limit)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find paste links in search results
            # Pastebin search results have links with class "i_p0" or in <li> tags
            paste_containers = soup.find_all('li', class_='gsc-result')  # Google Custom Search results
            if not paste_containers:
                # Try alternative structure
                paste_containers = soup.find_all('div', class_='gsc-webResult')
            
            if not paste_containers:
                # Pastebin might use simple list
                paste_links = soup.find_all('a', href=True)
                for link in paste_links:
                    href = link.get('href', '')
                    # Match pastebin.com/xxxxxxxx pattern
                    if 'pastebin.com/' in href and '/' in href.split('pastebin.com/')[-1]:
                        paste_id = href.split('pastebin.com/')[-1].split('/')[0]
                        if paste_id and len(paste_id) == 8 and paste_id.isalnum():
                            paste_url = f"https://pastebin.com/{paste_id}"
                            if paste_url not in self.discovered_urls:
                                discovered_urls.append(paste_url)
                                self.discovered_urls.add(paste_url)
                                logger.info(f"  ✓ Found: {paste_url}")
                                
                                if len(discovered_urls) >= limit:
                                    break
            else:
                # Parse Google Custom Search results
                for container in paste_containers:
                    link = container.find('a', href=True)
                    if link:
                        href = link.get('href', '')
                        if 'pastebin.com/' in href:
                            paste_id = href.split('pastebin.com/')[-1].split('/')[0].split('?')[0]
                            if paste_id and len(paste_id) == 8:
                                paste_url = f"https://pastebin.com/{paste_id}"
                                if paste_url not in self.discovered_urls:
                                    discovered_urls.append(paste_url)
                                    self.discovered_urls.add(paste_url)
                                    logger.info(f"  ✓ Found: {paste_url}")
                                    
                                    if len(discovered_urls) >= limit:
                                        break
            
            # If search didn't return results, fallback to archive scraping
            if not discovered_urls:
                logger.info("[PASTEBIN SEARCH] No results found, trying archive fallback...")
                return self._fallback_archive_search(keyword, limit)
            
            logger.info(f"[PASTEBIN SEARCH] Found {len(discovered_urls)} pastes")
            
        except Exception as e:
            logger.error(f"[PASTEBIN SEARCH] Error: {e}")
            # Fallback to archive search
            return self._fallback_archive_search(keyword, limit)
        
        return discovered_urls
    
    def _fallback_archive_search(self, keyword: str, limit: int = 50) -> List[str]:
        """
        Fallback method: Scrape recent archive and filter by keyword in content.
        This is slower but works when search is unavailable.
        
        Args:
            keyword: Search keyword
            limit: Maximum URLs to return
            
        Returns:
            List of paste URLs containing the keyword
        """
        discovered_urls = []
        
        try:
            logger.info(f"[ARCHIVE FALLBACK] Scraping recent pastes for: {keyword}")
            archive_url = "https://pastebin.com/archive"
            
            response = self._make_request(archive_url)
            if not response:
                logger.warning("[ARCHIVE FALLBACK] Failed to fetch archive")
                return discovered_urls
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find paste links in archive
            paste_links = soup.find_all('a', href=True)
            checked_count = 0
            
            for link in paste_links:
                href = link.get('href', '')
                
                # Match paste URL pattern (format: /xxxxxxxx)
                if href.startswith('/') and len(href) == 9 and href[1:].isalnum():
                    paste_url = f"https://pastebin.com{href}"
                    
                    if paste_url not in self.discovered_urls:
                        # Download and check content
                        paste_response = self._make_request(paste_url)
                        checked_count += 1
                        
                        if paste_response and keyword.lower() in paste_response.text.lower():
                            discovered_urls.append(paste_url)
                            self.discovered_urls.add(paste_url)
                            logger.info(f"  ✓ Match found: {paste_url}")
                            
                            if len(discovered_urls) >= limit:
                                break
                        
                        # Limit number of pastes checked to avoid rate limiting
                        if checked_count >= min(100, limit * 5):
                            logger.info(f"[ARCHIVE FALLBACK] Checked {checked_count} pastes, stopping")
                            break
            
            logger.info(f"[ARCHIVE FALLBACK] Found {len(discovered_urls)} matching pastes from {checked_count} checked")
            
        except Exception as e:
            logger.error(f"[ARCHIVE FALLBACK] Error: {e}")
        
        return discovered_urls
    
    def search_by_keywords(self, keywords: List[str], limit: int = 50) -> List[str]:
        """
        Automatically search multiple paste sites for keywords using their search functionality.
        
        Args:
            keywords: List of keywords to search for (e.g., ["ui.ac.id", "universitas indonesia"])
            limit: Maximum total URLs to discover
            
        Returns:
            List of discovered paste URLs
        """
        all_urls = []
        per_keyword_limit = max(10, limit // len(keywords)) if len(keywords) > 0 else limit
        
        for keyword in keywords:
            logger.info(f"[KEYWORD SEARCH] Searching for: {keyword}")
            
            # Search Pastebin using search functionality
            pastebin_urls = self.search_pastebin_by_keyword(keyword, limit=per_keyword_limit)
            all_urls.extend(pastebin_urls)
            
            logger.info(f"[KEYWORD SEARCH] Found {len(pastebin_urls)} pastes for '{keyword}'")
            
            # TODO: Add search for other paste sites (Paste.ee, Ghostbin, etc.)
            # Most paste sites don't have public search, but we can try archive scraping
            
            if len(all_urls) >= limit:
                break
            
            # Small delay between keyword searches to avoid rate limiting
            time.sleep(1)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in all_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"[KEYWORD SEARCH] Total discovered: {len(unique_urls)} unique URLs")
        return unique_urls[:limit]
    
    def search_darkweb_pastes(self, keywords: List[str], limit: int = 30) -> List[str]:
        """
        Search darkweb paste sites (via clearnet mirrors) for keywords.
        
        Note: This uses clearnet mirrors of darkweb sites. For actual .onion access,
        you need Tor proxy configured (TOR_PROXY_ENABLED=true).
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum URLs to discover
            
        Returns:
            List of discovered paste URLs from darkweb sources
        """
        if not DARKWEB_SOURCES:
            logger.warning("No darkweb sources configured")
            return []
        
        logger.info(f"[DARKWEB] Searching {len(DARKWEB_SOURCES)} darkweb paste sites")
        all_urls = []
        
        for source in DARKWEB_SOURCES:
            try:
                logger.info(f"[DARKWEB] Scraping: {source}")
                
                # Use Tor session if available, otherwise regular session
                session = self.tor_session if self.tor_session else self.session
                
                # Fetch recent pastes from darkweb site
                urls = self._scrape_darkweb_recent(source, session, keywords, limit // len(DARKWEB_SOURCES))
                all_urls.extend(urls)
                
                if len(all_urls) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"[DARKWEB] Failed to scrape {source}: {e}")
                continue
        
        logger.info(f"[DARKWEB] Total discovered URLs: {len(all_urls)}")
        return all_urls[:limit]
    
    def _scrape_darkweb_recent(self, base_url: str, session: requests.Session, keywords: List[str], limit: int = 10) -> List[str]:
        """
        Scrape recent pastes from a darkweb paste site.
        
        Args:
            base_url: Base URL of the darkweb paste site
            session: Request session to use (Tor or regular)
            keywords: Keywords to search for in paste content
            limit: Maximum pastes to return
            
        Returns:
            List of paste URLs containing keywords
        """
        discovered = []
        
        try:
            # Try common paste listing endpoints
            listing_paths = [
                "/recent",
                "/archive", 
                "/list",
                "/pastes",
                "/"  # Some sites list on homepage
            ]
            
            for path in listing_paths:
                try:
                    url = f"{base_url}{path}"
                    headers = {
                        'User-Agent': self._get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml',
                    }
                    
                    response = session.get(url, headers=headers, timeout=30)
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find paste links (common patterns)
                    paste_links = []
                    
                    # Pattern 1: /view/xxxxxx or /p/xxxxx
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')
                        if any(pattern in href for pattern in ['/view/', '/p/', '/paste/', '/show/']):
                            full_url = urljoin(base_url, href)
                            paste_links.append(full_url)
                    
                    # Check each paste for keywords
                    for paste_url in paste_links[:limit * 2]:  # Check more to find relevant ones
                        if paste_url in self.discovered_urls:
                            continue
                        
                        try:
                            paste_response = session.get(paste_url, headers=headers, timeout=20)
                            if paste_response.status_code == 200:
                                content = paste_response.text.lower()
                                
                                # Check if any keyword matches
                                if any(kw.lower() in content for kw in keywords):
                                    discovered.append(paste_url)
                                    self.discovered_urls.add(paste_url)
                                    logger.info(f"[DARKWEB] Found relevant paste: {paste_url}")
                                    
                                    if len(discovered) >= limit:
                                        return discovered
                            
                            # Rate limiting - darkweb sites are slower
                            time.sleep(REQUEST_DELAY * 2)
                            
                        except Exception as e:
                            logger.debug(f"[DARKWEB] Failed to fetch paste {paste_url}: {e}")
                            continue
                    
                    # If we found pastes in this path, don't try others
                    if paste_links:
                        break
                        
                except Exception as e:
                    logger.debug(f"[DARKWEB] Failed to access {url}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"[DARKWEB] Error scraping {base_url}: {e}")
        
        return discovered
        
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
        crawl_authors: bool = True,
        darkweb_keywords: List[str] = None
    ) -> Dict:
        """
        Run complete discovery across provided URLs and darkweb sources.
        
        Args:
            clearnet_urls: Initial list of paste URLs to analyze
            enable_clearnet: Whether to enable clearnet discovery
            enable_darknet: Whether to enable darknet paste searching
            crawl_authors: Whether to crawl paste authors' profiles
            darkweb_keywords: Keywords to search on darkweb (if None, uses clearnet_urls keywords)
            
        Returns:
            Dictionary with all results and metadata
        """
        logger.info("=" * 70)
        logger.info("NEXZY DISCOVERY ENGINE - STARTING SCAN")
        logger.info(f"Target Domain: {TARGET_DOMAIN}")
        logger.info(f"Clearnet: {enable_clearnet}, Darkweb: {enable_darknet}")
        logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"URLs to scan: {len(clearnet_urls) if clearnet_urls else 0}")
        logger.info("=" * 70)
        
        all_results = []
        darkweb_urls = []
        
        # Darkweb discovery (if enabled)
        if enable_darknet:
            try:
                logger.info("[DARKWEB] Starting darkweb paste discovery...")
                keywords = darkweb_keywords or [TARGET_DOMAIN]
                darkweb_urls = self.search_darkweb_pastes(keywords, limit=30)
                logger.info(f"[DARKWEB] Discovered {len(darkweb_urls)} darkweb paste URLs")
            except Exception as e:
                logger.error(f"[DARKWEB] Failed to search darkweb: {e}")
                darkweb_urls = []
        
        # Combine clearnet and darkweb URLs
        all_urls = (clearnet_urls or []) + darkweb_urls
        
        if not all_urls:
            logger.warning("No URLs to process (clearnet and darkweb both empty)")
            return {
                'discovered_items': all_results,
                'total_found': 0,
                'scan_time': datetime.utcnow().isoformat()
            }
        
        # Process all URLs (clearnet + darkweb)
        for url in all_urls:
            try:
                result = self.analyze_paste(url)
                if result:
                    all_results.append(result)
                    
                    # Optionally crawl author's other pastes
                    if crawl_authors and result['author'] != 'unknown':
                        # Only crawl clearnet authors (darkweb authors might not have profiles)
                        if not any(dweb in url for dweb in DARKWEB_SOURCES):
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
        logger.info(f"Clearnet URLs: {len(clearnet_urls or [])}, Darkweb URLs: {len(darkweb_urls)}")
        logger.info("=" * 70)
        
        return {
            'discovered_items': all_results,
            'total_found': len(all_results),
            'target_domain': TARGET_DOMAIN,
            'scan_time': datetime.utcnow().isoformat(),
            'urls_scanned': len(all_urls),
            'darkweb_urls_found': len(darkweb_urls)
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
