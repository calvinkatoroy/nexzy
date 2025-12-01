"""
Supabase Client Configuration for Nexzy Backend
Provides database connection and client instance
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "Missing Supabase credentials. Please set SUPABASE_URL and "
        "SUPABASE_SERVICE_ROLE_KEY in your .env file"
    )

# Initialize Supabase client with service role key (for backend operations)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_supabase() -> Client:
    """
    Dependency function to get Supabase client instance.
    Use this in FastAPI endpoints with Depends(get_supabase).
    
    Returns:
        Client: Configured Supabase client instance
    """
    return supabase
