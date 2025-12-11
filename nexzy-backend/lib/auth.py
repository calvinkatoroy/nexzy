"""
Authentication middleware for Nexzy Backend
Verifies JWT tokens from Supabase and provides user context
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from supabase import Client
from .supabase_client import get_supabase
from config import SUPABASE_URL
import base64
import json
import logging

logger = logging.getLogger(__name__)

# Security scheme for JWT Bearer tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> Dict:
    """
    Dependency to verify JWT token and extract user information.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token with Supabase
    3. Returns the authenticated user's data
    
    Args:
        credentials: JWT token from Authorization header
        supabase: Supabase client instance
        
    Returns:
        Dict: User data containing id, email, and other profile info
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        if not token:
            logger.error("Authentication error: Missing Bearer token in Authorization header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization Bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Debug: Compare token issuer to backend SUPABASE_URL (project alignment)
        try:
            parts = token.split('.')
            if len(parts) >= 2:
                payload_b64 = parts[1]
                # Pad base64 if needed
                padding = '=' * (-len(payload_b64) % 4)
                payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode('utf-8')
                payload = json.loads(payload_json)
                iss = payload.get('iss', '')
                backend_domain = SUPABASE_URL.split('//')[-1].split('/')[0]
                iss_domain = iss.split('//')[-1].split('/')[0] if iss else ''
                logger.info(f"Auth debug: token iss domain={iss_domain}, backend domain={backend_domain}")
        except Exception as e:
            logger.debug(f"Auth debug: failed to parse token issuer: {e}")
        
        # Verify token with Supabase
        try:
            user_response = supabase.auth.get_user(token)
        except Exception as e:
            # Log the token length and last 8 chars for traceability (avoid full token)
            safe_tail = token[-8:] if len(token) >= 8 else ""
            logger.error(f"Supabase get_user failed (token_len={len(token)}, tail=...{safe_tail}): {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user_response or not user_response.user:
            # Differentiate invalid vs missing user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_response.user
        
        # Return user data
        return {
            "id": user.id,
            "email": user.email,
            "user_metadata": user.user_metadata,
            "created_at": user.created_at
        }
        
    except HTTPException:
        # Already logged and raised above
        raise
    except Exception as e:
        logger.error(f"Authentication error (unexpected): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    supabase: Client = Depends(get_supabase)
) -> Optional[Dict]:
    """
    Optional authentication dependency.
    Returns user if authenticated, None otherwise.
    Useful for endpoints that can work with or without authentication.
    
    Args:
        credentials: Optional JWT token
        supabase: Supabase client instance
        
    Returns:
        Optional[Dict]: User data if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        
        if user_response and user_response.user:
            user = user_response.user
            return {
                "id": user.id,
                "email": user.email,
                "user_metadata": user.user_metadata,
                "created_at": user.created_at
            }
    except Exception as e:
        logger.warning(f"Optional auth failed: {str(e)}")
    
    return None
