"""
AI Service Client for Nexzy
Communicates with AI-Scoring-and-Summarizing service
"""

import httpx
import logging
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import AI_SERVICE_URL
except ImportError:
    # Fallback if config not available
    AI_SERVICE_URL = "http://localhost:8000"

logger = logging.getLogger(__name__)

async def analyze_batch(
    items: List[Dict[str, str]],
    score_threshold: float = 40.0,
    max_parallel_gemini: int = 16
) -> List[Dict]:
    """
    Send batch of texts to AI service for scoring and summarization.
    
    Args:
        items: List of dicts with keys: text, url, timestamp
        score_threshold: Minimum score to trigger summarization
        max_parallel_gemini: Max concurrent Gemini API calls
        
    Returns:
        List of analysis results with scores, summaries, rationales
    """
    # Check if AI service is disabled
    if not AI_SERVICE_URL or AI_SERVICE_URL.strip() == "":
        logger.info("AI service disabled (AI_SERVICE_URL not configured)")
        return [{
            "index": i,
            "vulnerability_score": 0.0,
            "summary": "AI service disabled",
            "rationale": "AI_SERVICE_URL not configured in .env",
            "alerts": "LOW",
            "signals": [],
            "mitigation": "AI service not configured. Enable AI_SERVICE_URL for automated mitigation recommendations."
        } for i in range(len(items))]
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/analyze_batch",
                json={
                    "items": items,
                    "score_threshold": score_threshold,
                    "max_parallel_gemini": max_parallel_gemini,
                    "max_summary_chars": 1200
                }
            )
            response.raise_for_status()
            data = response.json()
            # Prefer 'results' if provided by AI service
            if isinstance(data, dict) and "results" in data:
                return data["results"]
            # Some services may echo the request payload; synthesize minimal results
            items_echo = data.get("items") if isinstance(data, dict) else None
            if items_echo:
                synthesized = []
                for i, it in enumerate(items_echo):
                    synthesized.append({
                        "index": i,
                        "vulnerability_score": 0.0,
                        "summary": "AI service returned echo payload; no analysis provided",
                        "rationale": "Service did not return 'results' field",
                        "alerts": "LOW",
                        "signals": []
                    })
                return synthesized
            # Fallback when structure is unexpected
            return []
            
    except httpx.HTTPError as e:
        logger.error(f"AI service error: {e}")
        # Fallback: return empty analysis
        return [{
            "index": i,
            "vulnerability_score": 0.0,
            "summary": "AI service unavailable",
            "rationale": "Could not connect to AI scoring service",
            "alerts": "LOW",
            "signals": [],
            "mitigation": "AI service unavailable. Manual review recommended."
        } for i in range(len(items))]
    except Exception as e:
        logger.error(f"Unexpected error calling AI service: {e}")
        return []


async def score_single_text(text: str, url: Optional[str] = None) -> Dict:
    """
    Score a single text (convenience wrapper).
    
    Returns:
        Dict with vulnerability_score, summary, rationale, alerts
    """
    results = await analyze_batch([{"text": text, "url": url, "timestamp": None}])
    return results[0] if results else {
        "vulnerability_score": 0.0,
        "summary": "Analysis failed",
        "rationale": "Service unavailable",
        "alerts": "LOW",
        "signals": [],
        "mitigation": "Analysis failed. Manual review required."
    }
