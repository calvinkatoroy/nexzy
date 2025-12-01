"""
Sample test file for Nexzy Backend API
Run with: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment
os.environ["SKIP_CONFIG_VALIDATION"] = "true"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-key"

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nexzy API"
    assert data["version"] == "2.0.0"
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data


# Note: Authentication tests require a valid Supabase setup
# These are basic structure tests. Add integration tests with test database.

@pytest.mark.skip(reason="Requires valid Supabase authentication")
def test_create_scan_requires_auth():
    """Test that creating a scan requires authentication"""
    response = client.post("/api/scan", json={
        "urls": ["https://pastebin.com/test"],
        "enable_clearnet": True,
        "crawl_authors": False
    })
    assert response.status_code == 403  # Forbidden without auth


@pytest.mark.skip(reason="Requires valid Supabase authentication")
def test_list_scans_requires_auth():
    """Test that listing scans requires authentication"""
    response = client.get("/api/scans")
    assert response.status_code == 403  # Forbidden without auth


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
