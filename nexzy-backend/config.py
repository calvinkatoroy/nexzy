"""
Configuration module for Nexzy Backend
Loads environment variables and defines application constants
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==============================================================================
# SUPABASE CONFIGURATION
# ==============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

# ==============================================================================
# TARGET CONFIGURATION
# ==============================================================================

# Target domain for credential monitoring
TARGET_DOMAIN = os.getenv("TARGET_DOMAIN", "ui.ac.id")

# ==============================================================================
# SCRAPER CONFIGURATION
# ==============================================================================

# Request delays (in seconds)
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Relevance scoring - Lower = more sensitive (will show more results)
MIN_RELEVANCE_SCORE = float(os.getenv("MIN_RELEVANCE_SCORE", "0.05"))

# Leak detection keywords
LEAK_KEYWORDS = [
    "password", "credentials", "leaked", "database", "dump", 
    "breach", "hack", "compromised", "exposed", "confidential",
    "username", "passwd", "login", "account"
]

# User agents for web scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]

# Clearnet sources (paste sites)
CLEARNET_SOURCES = [
    "https://pastebin.com",
    "https://paste.ee",
    "https://privatebin.net",
    "https://justpaste.it",
    "https://pastelink.net"
]

# Darkweb sources (onion sites and public mirrors)
# Note: These are clearnet mirrors of darkweb paste sites
# Actual .onion sites require Tor proxy
DARKWEB_SOURCES = [
    "https://strongerw2ise74v3duebgsvug4mehyhlpa7f6kfwnas7zofs3kov7yd.onion.ly",  # Stronghold Paste mirror
    "https://paste2vljbekqqa3k555ihc2c4k62kzqjfbgvqk6zkupcdnlqsx4biqd.onion.pet",  # DarkPaste mirror
    "https://nzxj65x32vh2fkhk.onion.ws",  # OnionPaste mirror
]

# Tor proxy settings (optional - if you have Tor running)
TOR_PROXY_ENABLED = os.getenv("TOR_PROXY_ENABLED", "False").lower() == "true"
TOR_PROXY_URL = os.getenv("TOR_PROXY_URL", "socks5h://127.0.0.1:9050")

# ==============================================================================
# API CONFIGURATION
# ==============================================================================

# API server settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))

# AI Service Configuration
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8000")

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

# Log file location
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "nexzy_backend.log"

# Log level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==============================================================================
# WEBSOCKET CONFIGURATION
# ==============================================================================

# WebSocket settings
WS_HEARTBEAT_INTERVAL = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
WS_MAX_RECONNECT_ATTEMPTS = int(os.getenv("WS_MAX_RECONNECT_ATTEMPTS", "5"))

# ==============================================================================
# DEVELOPMENT MODE
# ==============================================================================

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ==============================================================================
# VALIDATION
# ==============================================================================

def validate_config():
    """
    Validate that all required configuration values are set.
    Raises ValueError if any required config is missing.
    """
    required_vars = {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": SUPABASE_SERVICE_ROLE_KEY,
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please check your .env file and ensure all required variables are set."
        )

# Run validation on import (can be disabled in tests)
if os.getenv("SKIP_CONFIG_VALIDATION") != "true":
    try:
        validate_config()
    except ValueError as e:
        if ENVIRONMENT == "production":
            raise
        else:
            print(f"⚠️  Configuration Warning: {e}")
