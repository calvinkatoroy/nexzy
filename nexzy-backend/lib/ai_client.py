"""
AI Service Client for Nexzy
Communicates with AI-Scoring-and-Summarizing service
"""

import httpx
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Default to localhost:8000 per integration request
AI_SERVICE_URL = "http://localhost:8000"

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
            "signals": []
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
        "signals": []
    }
