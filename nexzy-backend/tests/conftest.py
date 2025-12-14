"""
Pytest configuration and fixtures for Nexzy backend tests
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def test_user():
    """Mock user for testing"""
    return {
        "id": "test-user-id-12345",
        "email": "test@ui.ac.id",
        "created_at": "2024-01-01T00:00:00"
    }


@pytest.fixture
def test_scan_data():
    """Sample scan data for testing"""
    return {
        "query": "test@ui.ac.id",
        "scan_type": "email",
        "user_id": "test-user-id-12345"
    }


@pytest.fixture
def test_alert_data():
    """Sample alert data for testing"""
    return {
        "id": "alert-test-12345",
        "query": "test@ui.ac.id",
        "source": "Pastebin",
        "vulnerability_score": 88.5,
        "severity": "CRITICAL",
        "status": "new",
        "credentials_found": True
    }
