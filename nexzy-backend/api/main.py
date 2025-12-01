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

from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import logging
from datetime import datetime
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.supabase_client import get_supabase
from lib.auth import get_current_user, get_optional_user
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

# Create FastAPI app
app = FastAPI(
    title="Nexzy API",
    description="OSINT Intelligence Platform - Backend API",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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

class ScanRequest(BaseModel):
    """Request model for creating a new scan"""
    urls: List[str] = Field(..., description="List of paste URLs to scan", min_items=1)
    enable_clearnet: bool = Field(default=True, description="Enable clearnet discovery")
    enable_darknet: bool = Field(default=False, description="Enable darknet discovery")
    crawl_authors: bool = Field(default=True, description="Crawl paste authors' profiles")


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

def run_scan_task(
    scan_id: str, 
    user_id: str,
    scan_request: ScanRequest, 
    supabase: Client
):
    """
    Background task to execute the discovery scan.
    Updates database with progress and results.
    Frontend polls the database for updates (no WebSocket in background task).
    
    Args:
        scan_id: Unique identifier for this scan
        user_id: User who initiated the scan
        scan_request: Scan configuration
        supabase: Supabase client for database operations
    """
    try:
        logger.info(f"[START] Starting scan {scan_id} for user {user_id}")
        
        # Update scan status to 'running'
        supabase.table('scans').update({
            'status': 'running',
            'progress': 0.1,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', scan_id).execute()
        
        logger.info(f"[RUNNING] Scan {scan_id} status: running (10%)")
        
        # Update progress to 30%
        supabase.table('scans').update({
            'progress': 0.3,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', scan_id).execute()
        
        logger.info(f"[PROGRESS] Scan {scan_id} progress: 30%")
        
        # Initialize and run Discovery Orchestrator
        orchestrator = DiscoveryOrchestrator()
        
        logger.info(f"[DISCOVERY] Running discovery for {len(scan_request.urls)} URLs")
        results = orchestrator.run_full_discovery(
            clearnet_urls=scan_request.urls,
            enable_clearnet=scan_request.enable_clearnet,
            enable_darknet=scan_request.enable_darknet,
            crawl_authors=scan_request.crawl_authors
        )
        
        # Update progress to 70%
        supabase.table('scans').update({
            'progress': 0.7,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', scan_id).execute()
        
        logger.info(f"[PROGRESS] Scan {scan_id} progress: 70%")
        
        # Process and insert results into database
        discovered_items = results.get('discovered_items', [])
        total_results = len(discovered_items)
        credentials_found = 0
        
        logger.info(f"[RESULTS] Scan {scan_id} found {total_results} results")
        
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
            
            for result in results_response.data:
                try:
                    # Determine severity based on relevance score and target emails
                    target_email_count = len(result.get('target_emails', []))
                    relevance = result.get('relevance_score', 0.0)
                    
                    if target_email_count >= 5 or relevance >= 0.8:
                        severity = 'critical'
                    elif target_email_count >= 2 or relevance >= 0.6:
                        severity = 'high'
                    elif target_email_count >= 1 or relevance >= 0.4:
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    alert_data = {
                        'user_id': user_id,
                        'title': f"Data Leak Detected - {result.get('source', 'Unknown Source')}",
                        'description': f"Personal data leak detected from {result.get('author', 'unknown')} containing {target_email_count} target emails. Source URL: {result.get('url', 'N/A')}",
                        'severity': severity
                        # status will use database default
                    }
                    
                    supabase.table('alerts').insert(alert_data).execute()
                    alerts_created += 1
                    logger.info(f"  [OK] Alert created: {severity.upper()} - {alert_data['title']}")
                    
                except Exception as e:
                    logger.error(f"  [ERROR] Failed to create alert for result {result.get('id')}: {e}")
            
            logger.info(f"[DONE] Created {alerts_created} alerts from {credentials_found} credential leaks")
        
        # Update scan to completed with credentials count
        supabase.table('scans').update({
            'status': 'completed',
            'progress': 1.0,
            'total_results': total_results,
            'credentials_found': credentials_found,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', scan_id).execute()
        
        logger.info(f"[SUCCESS] Scan {scan_id} completed successfully - {total_results} results, {credentials_found} credentials, {alerts_created} alerts")
        
    except Exception as e:
        logger.error(f"[FAILED] Scan {scan_id} failed: {str(e)}")
        logger.exception(e)
        
        # Update scan status to failed
        try:
            supabase.table('scans').update({
                'status': 'failed',
                'error': str(e),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', scan_id).execute()
            
            logger.info(f"[DB] Updated scan {scan_id} status to failed")
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


@app.post("/api/scan", response_model=ScanResponse)
async def create_scan(
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
        
        # Add background task to run the scan
        logger.info(f"[TASK] Adding background task for scan {scan_id}")
        background_tasks.add_task(
            run_scan_task,
            scan_id=scan_id,
            user_id=user_id,
            scan_request=scan_request,
            supabase=supabase
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
async def list_scans(
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    List all scans for the authenticated user.
    Returns scans ordered by creation date (newest first).
    
    Args:
        current_user: Authenticated user from JWT token
        supabase: Supabase client instance
        
    Returns:
        List of ScanStatus objects
    """
    try:
        user_id = current_user['id']
        
        # Query scans from database
        response = supabase.table('scans')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
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


@app.get("/api/alerts")
async def list_alerts(
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    List all alerts for the authenticated user.
    Returns alerts ordered by creation date (newest first).
    
    Args:
        current_user: Authenticated user from JWT token
        supabase: Supabase client instance
        
    Returns:
        List of alert objects
    """
    try:
        user_id = current_user['id']
        
        # Query alerts from database
        response = supabase.table('alerts')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        
        return response.data
        
    except Exception as e:
        logger.error(f"Failed to list alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts: {str(e)}"
        )


@app.get("/api/search")
async def search_results(
    q: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[float] = None,
    has_credentials: Optional[bool] = None,
    email_domain: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Search scan results with filters.
    
    Query params:
        q: Keyword search in URL, content, author
        source: Filter by source (pastebin, github, etc)
        min_score: Minimum relevance score (0.0-1.0)
        has_credentials: Filter results with credentials
        email_domain: Filter by email domain
        
    Returns:
        List of matching scan results with alert IDs
    """
    try:
        user_id = current_user['id']
        
        # Get all user's alerts (which link to scan results via description URL)
        alerts_response = supabase.table('alerts')\
            .select('id, description')\
            .eq('user_id', user_id)\
            .execute()
        
        # Create URL to alert_id mapping
        url_to_alert = {}
        for alert in alerts_response.data:
            # Extract URL from description like "Source URL: https://..."
            desc = alert.get('description', '')
            if 'Source URL: ' in desc:
                url = desc.split('Source URL: ')[-1].strip()
                url_to_alert[url] = alert['id']
        
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
        
        # Execute query
        results_response = query.order('found_at', desc=True).execute()
        results = results_response.data
        
        # Add alert_id to each result
        for result in results:
            url = result.get('url')
            result['alert_id'] = url_to_alert.get(url, None)
        
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
        
        logger.info(f"Search returned {len(results)} results for user {user_id}")
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
        port=8000,
        log_level="info"
    )
