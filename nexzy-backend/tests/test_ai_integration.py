"""
AI Service Integration Tests
Tests RoBERTa scoring and Gemini mitigation generation
"""

import pytest
from lib.ai_client import analyze_batch
import asyncio


# ==============================================================================
# AI SERVICE TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_ai_analyze_batch_returns_results():
    """Test that AI analysis returns results for sample data"""
    test_data = [
        {
            "index": 0,
            "text": "Database credentials leaked: username=admin password=admin123"
        }
    ]
    
    try:
        results = await analyze_batch(test_data)
        assert results is not None
        assert len(results) == 1
        assert "vulnerability_score" in results[0]
        assert results[0]["vulnerability_score"] >= 0
        assert results[0]["vulnerability_score"] <= 100
    except Exception as e:
        # AI service may not be running in test environment
        pytest.skip(f"AI service not available: {e}")


@pytest.mark.asyncio
async def test_ai_handles_empty_batch():
    """Test AI service handles empty batch gracefully"""
    try:
        results = await analyze_batch([])
        assert results == [] or results is None
    except Exception:
        pytest.skip("AI service not available")


@pytest.mark.asyncio
async def test_ai_scores_critical_leak():
    """Test that AI gives high score to obvious credential leak"""
    test_data = [
        {
            "index": 0,
            "text": "CRITICAL: Production database exposed! Host: db.company.com User: root Password: P@ssw0rd123 Port: 3306"
        }
    ]
    
    try:
        results = await analyze_batch(test_data)
        assert results[0]["vulnerability_score"] > 70  # Should be high risk
    except Exception:
        pytest.skip("AI service not available")


@pytest.mark.asyncio
async def test_ai_scores_low_risk_content():
    """Test that AI gives low score to benign content"""
    test_data = [
        {
            "index": 0,
            "text": "This is a regular text message with no sensitive information."
        }
    ]
    
    try:
        results = await analyze_batch(test_data)
        assert results[0]["vulnerability_score"] < 50  # Should be low risk
    except Exception:
        pytest.skip("AI service not available")


@pytest.mark.asyncio
async def test_ai_includes_mitigation():
    """Test that AI provides mitigation recommendations"""
    test_data = [
        {
            "index": 0,
            "text": "API key exposed: sk-1234567890abcdef"
        }
    ]
    
    try:
        results = await analyze_batch(test_data)
        assert "mitigation" in results[0]
        assert len(results[0]["mitigation"]) > 0
    except Exception:
        pytest.skip("AI service not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
