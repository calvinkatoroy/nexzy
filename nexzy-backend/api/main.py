"""
Nexzy Backend - FastAPI Application
Production-ready backend for OSINT credential leak detection

Main endpoints:
- POST /api/scan: Create and trigger a new scan
- GET /api/scans: List user's scan history
- GET /api/results/{scan_id}: Get scan results
- WebSocket /ws: Real-time scan updates
- GET /health: Health check
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
import uuid
import logging
from datetime import datetime
import asyncio
import sys
import os
from urllib.parse import urlparse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.supabase_client import get_supabase
from lib.auth import get_current_user, get_optional_user
from lib.ai_client import analyze_batch as ai_analyze_batch
from scrapers.discovery_engine import DiscoveryOrchestrator
from config import CORS_ORIGINS, TARGET_DOMAIN
from supabase import Client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nexzy_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Nexzy API",
    description="OSINT Intelligence Platform - Backend API",
    version="2.0.0"
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["http://localhost:5174"],  # Add port 5174 for dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# WEBSOCKET CONNECTION MANAGER
# ==============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# ==============================================================================
# PYDANTIC MODELS
# ==============================================================================

class SettingsUpdateRequest(BaseModel):
    """Request model for updating user settings"""
    target_domain: Optional[str] = Field(default=None, description="Target domain to monitor (e.g., 'ui.ac.id')")
    target_keywords: Optional[List[str]] = Field(default=None, description="Keywords to search for", max_items=10)
    organization: Optional[str] = Field(default=None, description="Organization name")


class ScanRequest(BaseModel):
    """Request model for creating a new scan"""
    urls: Optional[List[str]] = Field(default=None, description="List of paste URLs to scan (optional if using keywords)", max_items=20)
    keywords: Optional[List[str]] = Field(default=None, description="Keywords to search for (e.g., ['ui.ac.id', 'universitas indonesia'])", max_items=5)
    auto_discover: bool = Field(default=False, description="Automatically discover pastes using keywords")
    enable_clearnet: bool = Field(default=True, description="Enable clearnet discovery")
    enable_darknet: bool = Field(default=False, description="Enable darknet discovery")
    crawl_authors: bool = Field(default=True, description="Crawl paste authors' profiles")
    
    @field_validator('urls')
    @classmethod
    def validate_urls(cls, urls: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that all URLs are properly formatted and from allowed sources"""
        if not urls:
            return urls
            
        allowed_domains = [
            'pastebin.com', 'paste.ee', 'privatebin.net',
            'justpaste.it', 'pastelink.net', 'rentry.co',
            'ghostbin.co', 'paste.ubuntu.com'
        ]
        
        validated_urls = []
        for url in urls:
            # Parse URL
            try:
                parsed = urlparse(url)
                
                # Check scheme
                if parsed.scheme not in ['http', 'https']:
                    raise ValueError(f"Invalid URL scheme: {url}. Only http/https allowed.")
                
                # Check domain
                domain = parsed.netloc.lower()
                # Remove www. prefix
                domain = domain.replace('www.', '')
                
                # Validate against allowed domains
                if not any(domain.endswith(allowed) for allowed in allowed_domains):
                    raise ValueError(f"Domain not allowed: {domain}. Allowed domains: {', '.join(allowed_domains)}")
                
                # Check for suspicious patterns (SSRF prevention)
                if '@' in url or parsed.netloc.startswith('localhost') or parsed.netloc.startswith('127.'):
                    raise ValueError(f"Suspicious URL pattern detected: {url}")
                
                validated_urls.append(url)
                
            except ValueError as e:
                raise ValueError(str(e))
            except Exception:
                raise ValueError(f"Invalid URL format: {url}")
        
        return validated_urls
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, keywords: Optional[List[str]]) -> Optional[List[str]]:
        """Validate keywords for auto-discovery"""
        if not keywords:
            return keywords
        
        # Clean and validate keywords
        cleaned = []
        for kw in keywords:
            kw = kw.strip()
            if len(kw) < 3:
                raise ValueError(f"Keyword too short: '{kw}'. Minimum 3 characters.")
            if len(kw) > 100:
                raise ValueError(f"Keyword too long: '{kw}'. Maximum 100 characters.")
            cleaned.append(kw)
        
        return cleaned
    
    def model_post_init(self, __context) -> None:
        """Validate that either urls or keywords+auto_discover are provided"""
        if not self.urls and not (self.keywords and self.auto_discover):
            raise ValueError("Must provide either 'urls' or 'keywords' with 'auto_discover=true'")


class ScanResponse(BaseModel):
    """Response model for scan creation"""
    scan_id: str
    status: str
    message: str
    created_at: str


class ScanStatus(BaseModel):
    """Model for scan status information"""
    scan_id: str
    status: str
    progress: float
    total_results: int
    created_at: str
    updated_at: str
    error: Optional[str] = None


class ScanResult(BaseModel):
    """Model for individual scan result"""
    id: str
    scan_id: str
    url: str
    source: str
    author: str
    relevance_score: float
    emails: List[str]
    target_emails: List[str]
    has_credentials: bool
    found_at: str


# ==============================================================================
# BACKGROUND TASK FUNCTION
# ==============================================================================

async def run_scan_task(
    scan_id: str, 
    user_id: str,
    scan_request: ScanRequest, 
    supabase: Client
):
    """
    Background task to execute the discovery scan.
    Updates database with progress and results.
    Broadcasts WebSocket messages for real-time updates.
    
    Args:
        scan_id: Unique identifier for this scan
        user_id: User who initiated the scan
        scan_request: Scan configuration
        supabase: Supabase client for database operations
    """
    scan_logs = []  # Store scan logs for display
    
    def log_and_store(message: str, level: str = "INFO"):
        """Log message and store for frontend display"""
        logger.info(message)
        scan_logs.append({
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message
        })
    
    try:
        log_and_store(f"[START] Starting scan {scan_id} for user {user_id}")
        
        # Update scan status to 'running'
        supabase.table('scans').update({
            'status': 'running',
            'progress': 0.1,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', scan_id).execute()
        
        # Broadcast scan started
        await manager.broadcast({
            'type': 'scan_update',
            'data': {
                'scan_id': scan_id,
                'status': 'running',
                'progress': 0.1,
                'message': 'Scan started successfully'
            }
        })
        
        log_and_store(f"[RUNNING] Scan {scan_id} status: running (10%)")
        
        # Update progress to 30%
        supabase.table('scans').update({
            'progress': 0.3,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', scan_id).execute()
        
        await manager.broadcast({
            'type': 'scan_update',
            'data': {'scan_id': scan_id, 'status': 'running', 'progress': 0.3, 'message': 'Initializing discovery engine'}
        })
        
        log_and_store(f"[PROGRESS] Scan {scan_id} progress: 30%")
        
        # Initialize and run Discovery Orchestrator
        orchestrator = DiscoveryOrchestrator()
        
        # Auto-discover URLs if keywords provided
        urls_to_scan = scan_request.urls or []
        
        if scan_request.auto_discover and scan_request.keywords:
            log_and_store(f"[AUTO-DISCOVER] Searching for keywords: {scan_request.keywords}")
            discovered_urls = orchestrator.search_by_keywords(
                keywords=scan_request.keywords,
                limit=50  # Discover up to 50 relevant pastes
            )
            urls_to_scan.extend(discovered_urls)
            log_and_store(f"[AUTO-DISCOVER] Found {len(discovered_urls)} relevant URLs")
            
            # Update progress
            supabase.table('scans').update({
                'progress': 0.4,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', scan_id).execute()
            
            await manager.broadcast({
                'type': 'scan_update',
                'data': {'scan_id': scan_id, 'status': 'running', 'progress': 0.4, 'message': f'Discovered {len(discovered_urls)} URLs'}
            })
        
        if not urls_to_scan:
            raise Exception("No URLs to scan. Auto-discovery found no relevant pastes.")
        
        log_and_store(f"[DISCOVERY] Running discovery for {len(urls_to_scan)} URLs (Darknet: {scan_request.enable_darknet})")
        results = orchestrator.run_full_discovery(
            clearnet_urls=urls_to_scan,
            enable_clearnet=scan_request.enable_clearnet,
            enable_darknet=scan_request.enable_darknet,
            crawl_authors=scan_request.crawl_authors,
            darkweb_keywords=scan_request.keywords if scan_request.enable_darknet else None
        )
        
        # Update progress to 70%
        supabase.table('scans').update({
            'progress': 0.7,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', scan_id).execute()
        
        await manager.broadcast({
            'type': 'scan_update',
            'data': {'scan_id': scan_id, 'status': 'running', 'progress': 0.7, 'message': 'Analyzing results'}
        })
        
        log_and_store(f"[PROGRESS] Scan {scan_id} progress: 70%")
        
        # Process and insert results into database
        discovered_items = results.get('discovered_items', [])
        total_results = len(discovered_items)
        credentials_found = 0
        
        log_and_store(f"[RESULTS] Scan {scan_id} found {total_results} results")
        
        # Insert results into scan_results table
        for item in discovered_items:
            # Count credentials found
            has_creds = item.get('has_credentials', False)
            if has_creds:
                credentials_found += 1
            
            result_data = {
                'id': str(uuid.uuid4()),
                'scan_id': scan_id,
                'user_id': user_id,
                'url': item.get('url', ''),
                'source': item.get('source', 'pastebin'),
                'author': item.get('author', 'unknown'),
                'relevance_score': item.get('relevance_score', 0.0),
                'emails': item.get('emails', []),
                'target_emails': item.get('target_emails', []),
                'has_credentials': has_creds,
                'found_at': datetime.utcnow().isoformat()
            }
            
            try:
                supabase.table('scan_results').insert(result_data).execute()
            except Exception as e:
                logger.error(f"[ERROR] Failed to insert result: {e}")
        
        logger.info(f"[CREDENTIALS] Scan {scan_id} found {credentials_found} credentials")
        
        # === AI SCORING & SUMMARIZATION ===
        # Prepare data for AI analysis
        if credentials_found > 0:
            logger.info(f"[AI] Preparing {credentials_found} items for AI analysis...")
            
            ai_items = []
            for item in discovered_items:
                if item.get('has_credentials', False):
                    # Get content preview (first 1200 chars)
                    content = item.get('content_preview', '')[:1200]
                    ai_items.append({
                        "text": content,
                        "url": item.get('url', ''),
                        "timestamp": item.get('found_at', '')
                    })
            
                # Call AI service for batch analysis
                try:
                    ai_results = await ai_analyze_batch(
                        items=ai_items,
                        score_threshold=40.0,  # Only summarize if score >= 40
                        max_parallel_gemini=8
                    )
                    logger.info(f"[AI] Received {len(ai_results)} AI analysis results")
                except Exception as e:
                    logger.error(f"[AI] Analysis failed: {e}")
                    ai_results = []
        else:
            ai_results = []
        
        # Create alerts for results with credentials
        alerts_created = 0
        if credentials_found > 0:
            logger.info(f"[ALERTS] Creating alerts for {credentials_found} credential leaks...")
            
            # Query the scan results we just inserted
            results_response = supabase.table('scan_results')\
                .select('*')\
                .eq('scan_id', scan_id)\
                .eq('has_credentials', True)\
                .execute()
            
            # Create mapping of AI results by index
            ai_results_map = {ai_res.get('index', i): ai_res for i, ai_res in enumerate(ai_results)}
            
            for idx, result in enumerate(results_response.data):
                try:
                    # Get AI analysis if available
                    ai_data = ai_results_map.get(idx, {})
                    ai_score = ai_data.get('vulnerability_score', 0.0)
                    ai_summary = ai_data.get('summary', '')
                    ai_rationale = ai_data.get('rationale', '')
                    ai_alert_level = ai_data.get('alerts', 'LOW')
                    ai_signals = ai_data.get('signals', [])
                    ai_mitigation = ai_data.get('mitigation', '')
                    
                    # Determine severity based on AI score (if available) + target emails
                    target_email_count = len(result.get('target_emails', []))
                    relevance = result.get('relevance_score', 0.0)
                    
                    # Use AI score if available, otherwise fallback to heuristic
                    if ai_score > 0:
                        if ai_score >= 80 or ai_alert_level == 'HIGH':
                            severity = 'critical'
                        elif ai_score >= 50 or ai_alert_level == 'MEDIUM':
                            severity = 'high'
                        elif ai_score >= 30:
                            severity = 'medium'
                        else:
                            severity = 'low'
                    else:
                        # Fallback heuristic
                        if target_email_count >= 5 or relevance >= 0.8:
                            severity = 'critical'
                        elif target_email_count >= 2 or relevance >= 0.6:
                            severity = 'high'
                        elif target_email_count >= 1 or relevance >= 0.4:
                            severity = 'medium'
                        else:
                            severity = 'low'
                    
                    # Build description with AI insights
                    description = f"Personal data leak detected from {result.get('author', 'unknown')} containing {target_email_count} target emails."
                    
                    if ai_summary:
                        description += f"\n\nAI Summary: {ai_summary}"
                    
                    if ai_rationale:
                        description += f"\n\nRisk Assessment: {ai_rationale}"
                    
                    if ai_signals:
                        description += f"\n\nDetected Signals: {', '.join(ai_signals)}"
                    
                    if ai_mitigation:
                        description += f"\n\n🛡️ MITIGATION RECOMMENDATIONS:\n{ai_mitigation}"
                    
                    description += f"\n\nSource URL: {result.get('url', 'N/A')}"
                    
                    if ai_score > 0:
                        description += f"\n\nVulnerability Score: {ai_score:.1f}/100"
                    
                    alert_data = {
                        'user_id': user_id,
                        'title': f"Data Leak Detected - {result.get('source', 'Unknown Source')} (AI Score: {ai_score:.0f})" if ai_score > 0 else f"Data Leak Detected - {result.get('source', 'Unknown Source')}",
                        'description': description,
                        'severity': severity
                        # status will use database default
                    }
                    
                    supabase.table('alerts').insert(alert_data).execute()
                    alerts_created += 1
                    
                    if ai_score > 0:
                        logger.info(f"  [OK] Alert created: {severity.upper()} - AI Score: {ai_score:.1f} - {alert_data['title']}")
                    else:
                        logger.info(f"  [OK] Alert created: {severity.upper()} - {alert_data['title']}")
                    
                except Exception as e:
                    logger.error(f"  [ERROR] Failed to create alert for result {result.get('id')}: {e}")
            
            logger.info(f"[DONE] Created {alerts_created} alerts from {credentials_found} credential leaks")
        
        # Update scan to completed with credentials count and logs
        supabase.table('scans').update({
            'status': 'completed',
            'progress': 1.0,
            'total_results': total_results,
            'credentials_found': credentials_found,
            'logs': scan_logs,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', scan_id).execute()
        
        log_and_store(f"[SUCCESS] Scan {scan_id} completed successfully - {total_results} results, {credentials_found} credentials, {alerts_created} alerts")
        
        # Broadcast scan completed
        await manager.broadcast({
            'type': 'scan_update',
            'data': {
                'scan_id': scan_id,
                'status': 'completed',
                'progress': 1.0,
                'total_results': total_results,
                'credentials_found': credentials_found,
                'message': f'Scan completed! Found {credentials_found} credentials in {total_results} results'
            }
        })
        
    except Exception as e:
        log_and_store(f"[FAILED] Scan {scan_id} failed: {str(e)}", "ERROR")
        logger.exception(e)
        
        # Update scan status to failed
        try:
            supabase.table('scans').update({
                'status': 'failed',
                'error': str(e),
                'logs': scan_logs,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', scan_id).execute()
            
            log_and_store(f"[DB] Updated scan {scan_id} status to failed")
            
            # Broadcast scan failed
            await manager.broadcast({
                'type': 'scan_update',
                'data': {
                    'scan_id': scan_id,
                    'status': 'failed',
                    'progress': 0,
                    'message': f'Scan failed: {str(e)}'
                }
            })
        except Exception as db_error:
            logger.error(f"[ERROR] Failed to update scan failure status: {db_error}")


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Nexzy API",
        "version": "2.0.0",
        "status": "operational",
        "target_domain": TARGET_DOMAIN,
        "endpoints": {
            "scans": "/api/scans",
            "create_scan": "POST /api/scan",
            "results": "/api/results/{scan_id}",
            "websocket": "/ws",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check(supabase: Client = Depends(get_supabase)):
    """
    Health check endpoint.
    Verifies API and database connectivity.
    """
    try:
        # Test database connection
        supabase.table('scans').select('id').limit(1).execute()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "websocket_connections": len(manager.active_connections)
    }


@app.get("/api/stats")
async def get_stats(
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Aggregated dashboard statistics for the frontend.

    Returns counts for:
    - alerts_total, alerts_critical, alerts_high, alerts_medium, alerts_low
    - alerts_resolved, alerts_open
    - credentials_leaked (number of scan_results with has_credentials=True)
    - new_alerts (alerts created in the last 24h)
    """
    try:
        user_id = current_user['id']

        # Alerts totals by severity
        alerts_resp = supabase.table('alerts')\
            .select('id, severity, status, created_at')\
            .eq('user_id', user_id)\
            .execute()

        alerts = alerts_resp.data or []
        alerts_total = len(alerts)
        alerts_critical = sum(1 for a in alerts if (a.get('severity') or '').lower() == 'critical')
        alerts_high = sum(1 for a in alerts if (a.get('severity') or '').lower() == 'high')
        alerts_medium = sum(1 for a in alerts if (a.get('severity') or '').lower() == 'medium')
        alerts_low = sum(1 for a in alerts if (a.get('severity') or '').lower() == 'low')

        # Resolved/open status (assuming status field stores lifecycle like 'open'/'resolved')
        alerts_resolved = sum(1 for a in alerts if (a.get('status') or '').lower() == 'resolved')
        alerts_open = alerts_total - alerts_resolved

        # New alerts in last 24 hours
        now = datetime.utcnow()
        def is_recent(created_at: str) -> bool:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                return (now - dt).total_seconds() <= 24 * 3600
            except Exception:
                return False
        new_alerts = sum(1 for a in alerts if a.get('created_at') and is_recent(a['created_at']))

        # Credentials leaked: count scan_results with has_credentials=True for user's scans
        scans_resp = supabase.table('scans')\
            .select('id')\
            .eq('user_id', user_id)\
            .execute()
        scan_ids = [s['id'] for s in (scans_resp.data or [])]

        credentials_leaked = 0
        if scan_ids:
            sr_resp = supabase.table('scan_results')\
                .select('id, has_credentials')\
                .in_('scan_id', scan_ids)\
                .eq('has_credentials', True)\
                .execute()
            credentials_leaked = len(sr_resp.data or [])

        return {
            'alerts_total': alerts_total,
            'alerts_critical': alerts_critical,
            'alerts_high': alerts_high,
            'alerts_medium': alerts_medium,
            'alerts_low': alerts_low,
            'alerts_resolved': alerts_resolved,
            'alerts_open': alerts_open,
            'new_alerts': new_alerts,
            'credentials_leaked': credentials_leaked,
        }
    except Exception as e:
        logger.error(f"Failed to compute stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to compute stats")


@app.get("/api/settings")
@limiter.limit("30/minute")
async def get_user_settings(
    request: Request,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get user's monitoring settings (target domain, keywords, etc.)"""
    try:
        user_id = current_user['id']
        response = supabase.table('user_profiles').select('*').eq('id', user_id).single().execute()
        
        if response.data:
            return response.data
        else:
            # Create default profile
            default = {'id': user_id, 'email': current_user.get('email'), 
                      'target_domain': 'ui.ac.id', 'target_keywords': ['ui.ac.id', 'universitas indonesia']}
            supabase.table('user_profiles').insert(default).execute()
            return default
    except Exception as e:
        logger.error(f"Failed to get settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve settings")


@app.put("/api/settings")
@limiter.limit("10/minute")
async def update_user_settings(
    request: Request,
    settings: SettingsUpdateRequest,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update user's monitoring settings"""
    try:
        user_id = current_user['id']
        update_data = {'updated_at': datetime.utcnow().isoformat()}
        
        if settings.target_domain:
            if len(settings.target_domain) < 3 or '.' not in settings.target_domain:
                raise HTTPException(status_code=400, detail="Invalid domain format")
            update_data['target_domain'] = settings.target_domain.lower()
        
        if settings.target_keywords is not None:
            if len(settings.target_keywords) > 10:
                raise HTTPException(status_code=400, detail="Maximum 10 keywords allowed")
            update_data['target_keywords'] = settings.target_keywords
        
        if settings.organization:
            update_data['organization'] = settings.organization
        
        response = supabase.table('user_profiles').update(update_data).eq('id', user_id).execute()
        
        if not response.data:
            # Create new profile if doesn't exist
            profile = {
                'id': user_id, 
                'email': current_user.get('email'), 
                'target_domain': settings.target_domain or 'ui.ac.id', 
                'target_keywords': settings.target_keywords or ['ui.ac.id'],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            if settings.organization:
                profile['organization'] = settings.organization
            response = supabase.table('user_profiles').insert(profile).execute()
        
        return {"success": True, "data": response.data[0] if response.data else None}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update settings")


@app.post("/api/scan/quick")
@limiter.limit("5/minute")
async def quick_scan(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    ONE-CLICK QUICK SCAN
    Automatically starts a scan using user's configured settings.
    Perfect for a "Scan Now" button!
    """
    try:
        user_id = current_user['id']
        
        # Get user's settings
        settings_response = supabase.table('user_profiles').select('target_domain, target_keywords').eq('id', user_id).single().execute()
        
        if settings_response.data:
            target_domain = settings_response.data.get('target_domain', 'ui.ac.id')
            target_keywords = settings_response.data.get('target_keywords', ['ui.ac.id', 'universitas indonesia'])
        else:
            target_domain = 'ui.ac.id'
            target_keywords = ['ui.ac.id', 'universitas indonesia']
        
        # Create scan request automatically
        scan_request = ScanRequest(keywords=target_keywords, auto_discover=True, crawl_authors=True)
        scan_id = str(uuid.uuid4())
        
        logger.info(f"🚀 QUICK SCAN: {scan_id} for {user_id} - Target: {target_domain}")
        
        # Create scan record
        scan_data = {
            'id': scan_id, 'user_id': user_id, 'status': 'queued', 'progress': 0.0,
            'total_results': 0, 'credentials_found': 0, 'urls': [],
            'options': {'quick_scan': True, 'target_domain': target_domain, 'keywords': target_keywords,
                       'auto_discover': True, 'crawl_authors': True},
            'created_at': datetime.utcnow().isoformat(), 'updated_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('scans').insert(scan_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create scan")
        
        # Schedule background task
        asyncio.create_task(run_scan_task(scan_id=scan_id, user_id=user_id, scan_request=scan_request, supabase=supabase))
        
        return ScanResponse(scan_id=scan_id, status='queued', 
                          message=f'Quick scan started! Monitoring {target_domain} for leaks...', 
                          created_at=datetime.utcnow().isoformat())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Quick scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quick scan failed: {str(e)}")


@app.post("/api/scan", response_model=ScanResponse)
@limiter.limit("5/minute")
async def create_scan(
    request: Request,
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Create a new scan and trigger background processing.
    
    This endpoint:
    1. Validates the user is authenticated
    2. Creates a scan record in the database
    3. Triggers a background task to run the discovery
    4. Returns immediately with the scan_id
    
    Args:
        scan_request: Scan configuration with URLs and options
        background_tasks: FastAPI background task manager
        current_user: Authenticated user from JWT token
        supabase: Supabase client instance
        
    Returns:
        ScanResponse with scan_id and initial status
    """
    try:
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        user_id = current_user['id']
        
        logger.info(f"🚀 POST /api/scan - Creating scan {scan_id} for user {user_id}")
        logger.info(f"📝 URLs: {scan_request.urls}")
        
        # Create scan record in database
        scan_data = {
            'id': scan_id,
            'user_id': user_id,
            'status': 'queued',
            'progress': 0.0,
            'total_results': 0,
            'credentials_found': 0,
            'urls': scan_request.urls,
            'options': {
                'enable_clearnet': scan_request.enable_clearnet,
                'enable_darknet': scan_request.enable_darknet,
                'crawl_authors': scan_request.crawl_authors
            },
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"💾 Inserting scan to database...")
        result = supabase.table('scans').insert(scan_data).execute()
        
        if not result.data:
            logger.error("❌ Database insert returned no data!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create scan in database"
            )
        
        logger.info(f"[DB] Scan inserted to database: {result.data}")
        
        # Schedule async background task directly on the running event loop
        logger.info(f"[TASK] Scheduling async background task for scan {scan_id}")
        asyncio.create_task(
            run_scan_task(
                scan_id=scan_id,
                user_id=user_id,
                scan_request=scan_request,
                supabase=supabase
            )
        )
        
        logger.info(f"[QUEUED] Scan {scan_id} queued successfully")
        
        return ScanResponse(
            scan_id=scan_id,
            status='queued',
            message='Scan created and queued for processing',
            created_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create scan: {str(e)}")
        logger.exception(e)  # Print full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scan: {str(e)}"
        )


@app.get("/api/scans", response_model=List[ScanStatus])
@limiter.limit("30/minute")
async def list_scans(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    List all scans for the authenticated user with pagination.
    Returns scans ordered by creation date (newest first).
    
    Args:
        request: FastAPI request object (for rate limiting)
        limit: Maximum number of scans to return (default: 50, max: 100)
        offset: Number of scans to skip (default: 0)
        current_user: Authenticated user from JWT token
        supabase: Supabase client instance
        
    Returns:
        List of ScanStatus objects
    """
    try:
        user_id = current_user['id']
        
        # Validate and cap limit
        limit = min(limit, 100) if limit > 0 else 50
        offset = max(offset, 0)
        
        # Query scans from database with pagination
        response = supabase.table('scans')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        scans = []
        for scan in response.data:
            scans.append(ScanStatus(
                scan_id=scan['id'],
                status=scan['status'],
                progress=scan.get('progress', 0.0),
                total_results=scan.get('total_results', 0),
                created_at=scan['created_at'],
                updated_at=scan['updated_at'],
                error=scan.get('error')
            ))
        
        return scans
        
    except Exception as e:
        logger.error(f"Failed to list scans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scans: {str(e)}"
        )


@app.get("/api/scans/{scan_id}")
@limiter.limit("30/minute")
async def get_scan_by_id(
    request: Request,
    scan_id: str,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Get a specific scan by ID with full details including logs.
    
    Args:
        request: FastAPI request object (for rate limiting)
        scan_id: Unique identifier for the scan
        current_user: Authenticated user from JWT token
        supabase: Supabase client instance
        
    Returns:
        Complete scan object including logs
    """
    try:
        user_id = current_user['id']
        
        # Query scan from database
        response = supabase.table('scans')\
            .select('*')\
            .eq('id', scan_id)\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found"
            )
        
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scans: {str(e)}"
        )


@app.get("/api/alerts")
@limiter.limit("30/minute")
async def list_alerts(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    severity: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    List all alerts for the authenticated user with pagination.
    Returns alerts ordered by creation date (newest first).
    
    Args:
        request: FastAPI request object (for rate limiting)
        limit: Maximum number of alerts to return (default: 50, max: 100)
        offset: Number of alerts to skip (default: 0)
        severity: Filter by severity (low, medium, high, critical)
        current_user: Authenticated user from JWT token
        supabase: Supabase client instance
        
    Returns:
        List of alert objects
    """
    try:
        user_id = current_user['id']
        
        # Validate and cap limit
        limit = min(limit, 100) if limit > 0 else 50
        offset = max(offset, 0)
        
        # Build query
        query = supabase.table('alerts')\
            .select('*')\
            .eq('user_id', user_id)
        
        # Apply severity filter if provided
        if severity:
            query = query.eq('severity', severity.lower())
        
        # Apply pagination and ordering
        response = query.order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return response.data
        
    except Exception as e:
        logger.error(f"Failed to list alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts: {str(e)}"
        )


@app.get("/api/search")
@limiter.limit("30/minute")
async def search_results(
    request: Request,
    q: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[float] = None,
    has_credentials: Optional[bool] = None,
    email_domain: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Search scan results with filters and pagination.
    
    Query params:
        request: FastAPI request object (for rate limiting)
        q: Keyword search in URL, content, author
        source: Filter by source (pastebin, github, etc)
        min_score: Minimum relevance score (0.0-1.0)
        has_credentials: Filter results with credentials
        email_domain: Filter by email domain
        limit: Maximum results to return (default: 50, max: 100)
        offset: Number of results to skip (default: 0)
        
    Returns:
        List of matching scan results with alert IDs
    """
    try:
        user_id = current_user['id']
        
        # Validate and cap limit
        limit = min(limit, 100) if limit > 0 else 50
        offset = max(offset, 0)
        
        # Get all user's alerts (which link to scan results via description URL)
        alerts_response = supabase.table('alerts')\
            .select('id, description')\
            .eq('user_id', user_id)\
            .execute()
        
        # Create URL to alert_id mapping (robust parsing)
        url_to_alert = {}
        for alert in alerts_response.data:
            desc = alert.get('description', '') or ''
            # Preferred: exact prefix match
            if 'Source URL: ' in desc:
                url = desc.split('Source URL: ')[-1].strip()
                if url:
                    url_to_alert[url] = alert['id']
                    continue
            # Fallback: find first http(s) URL substring
            import re
            try:
                m = re.search(r'https?://\S+', desc)
                if m:
                    extracted = m.group(0)
                    # Trim common trailing punctuation
                    extracted = extracted.rstrip(")'\"]")
                    url_to_alert[extracted] = alert['id']
            except Exception:
                pass
        
        # Get all user's scans
        scans_response = supabase.table('scans')\
            .select('id')\
            .eq('user_id', user_id)\
            .execute()
        
        scan_ids = [scan['id'] for scan in scans_response.data]
        
        if not scan_ids:
            return []
        
        # Build query
        query = supabase.table('scan_results')\
            .select('*')\
            .in_('scan_id', scan_ids)
        
        # Apply filters
        if source:
            query = query.eq('source', source)
        
        if min_score is not None:
            query = query.gte('relevance_score', min_score)
        
        if has_credentials is not None:
            query = query.eq('has_credentials', has_credentials)
        
        # Execute query with pagination
        results_response = query.order('found_at', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        results = results_response.data
        
        # Add alert_id to each result (exact match), else try normalized
        for result in results:
            url = (result.get('url') or '').strip()
            alert_id = url_to_alert.get(url)
            if not alert_id and url:
                # Normalize by removing trailing slashes
                url_norm = url.rstrip('/')
                # Try matching any mapping key that equals normalized
                for mapped_url, a_id in url_to_alert.items():
                    if mapped_url.rstrip('/') == url_norm:
                        alert_id = a_id
                        break
            result['alert_id'] = alert_id
        
        # Apply keyword search (post-filter since Supabase doesn't have LIKE for arrays)
        if q:
            q_lower = q.lower()
            results = [
                r for r in results
                if (q_lower in r.get('url', '').lower() or
                    q_lower in r.get('author', '').lower() or
                    q_lower in r.get('content_preview', '').lower())
            ]
        
        # Apply email domain filter (post-filter)
        if email_domain:
            domain_lower = email_domain.lower()
            results = [
                r for r in results
                if any(domain_lower in email.lower() for email in r.get('target_emails', []))
            ]
        
        logger.info(f"Search returned {len(results)} results for user {user_id} (limit={limit}, offset={offset})")
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/api/results/{scan_id}")
async def get_scan_results(
    scan_id: str,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Get results for a specific scan.
    
    Args:
        scan_id: Unique scan identifier
        current_user: Authenticated user from JWT token
        supabase: Supabase client instance
        
    Returns:
        Scan metadata and list of discovered results
    """
    try:
        user_id = current_user['id']
        
        # Verify scan exists and belongs to user
        scan_response = supabase.table('scans')\
            .select('*')\
            .eq('id', scan_id)\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        if not scan_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        scan = scan_response.data
        
        # Check if scan is completed
        if scan['status'] != 'completed':
            return {
                'scan_id': scan_id,
                'status': scan['status'],
                'progress': scan.get('progress', 0.0),
                'message': f"Scan is {scan['status']}. Results not yet available.",
                'results': []
            }
        
        # Fetch results from scan_results table
        results_response = supabase.table('scan_results')\
            .select('*')\
            .eq('scan_id', scan_id)\
            .order('relevance_score', desc=True)\
            .execute()
        
        results = []
        for result in results_response.data:
            results.append(ScanResult(
                id=result['id'],
                scan_id=result['scan_id'],
                url=result['url'],
                source=result['source'],
                author=result['author'],
                relevance_score=result['relevance_score'],
                emails=result.get('emails', []),
                target_emails=result.get('target_emails', []),
                has_credentials=result.get('has_credentials', False),
                found_at=result['found_at']
            ))
        
        return {
            'scan_id': scan_id,
            'status': scan['status'],
            'total_results': len(results),
            'created_at': scan['created_at'],
            'completed_at': scan['updated_at'],
            'results': results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scan results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve results: {str(e)}"
        )


# ==============================================================================
# WEBSOCKET ENDPOINT
# ==============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time scan updates.
    
    Clients connect to receive:
    - scan_started: When a scan begins
    - scan_progress: Progress updates during scan
    - scan_completed: When scan finishes successfully
    - scan_failed: If scan encounters an error
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            
            # Respond to ping for heartbeat
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ==============================================================================
# APPLICATION STARTUP
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("=" * 70)
    logger.info("NEXZY BACKEND STARTING")
    logger.info(f"Target Domain: {TARGET_DOMAIN}")
    logger.info(f"CORS Origins: {CORS_ORIGINS}")
    logger.info("=" * 70)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Nexzy backend shutting down")


# ==============================================================================
# RUN APPLICATION
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )
