"""
AI Scoring and Summarizing Service for Nexzy
Uses Google Gemini API for vulnerability analysis and mitigation recommendations
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import google.generativeai as genai
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Nexzy AI Scoring Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info("✅ Gemini API configured successfully")
else:
    logger.warning("⚠️ GEMINI_API_KEY not set - service will return mock data")

# Models
class TextItem(BaseModel):
    text: str
    url: Optional[str] = None
    timestamp: Optional[str] = None

class AnalyzeRequest(BaseModel):
    items: List[Dict]
    score_threshold: float = Field(default=40.0, ge=0, le=100)
    max_parallel_gemini: int = Field(default=16, ge=1, le=50)
    max_summary_chars: int = Field(default=1200, ge=100, le=5000)

class AnalysisResult(BaseModel):
    index: int
    vulnerability_score: float
    summary: str
    rationale: str
    alerts: str
    signals: List[str]
    mitigation: str  # NEW: Mitigation recommendations

# Gemini Analysis
async def analyze_with_gemini(text: str, url: Optional[str], index: int) -> Dict:
    """Analyze text using Gemini API with scoring and mitigation recommendations"""
    
    if not GEMINI_API_KEY:
        # Mock response for testing
        return {
            "index": index,
            "vulnerability_score": 65.0,
            "summary": "Mock Analysis - GEMINI_API_KEY not configured",
            "rationale": "This is a mock response. Configure GEMINI_API_KEY to enable real AI analysis.",
            "alerts": "MEDIUM",
            "signals": ["credentials", "emails", "passwords"],
            "mitigation": "Mock mitigation - Set GEMINI_API_KEY environment variable for real recommendations."
        }
    
    try:
        prompt = f"""You are a cybersecurity expert analyzing data leaks. Analyze this paste/content:

URL: {url or 'Unknown'}
Content:
{text[:3000]}  # Limit to first 3000 chars

Provide a structured analysis:

1. VULNERABILITY SCORE (0-100):
   - 0-20: Low risk (no sensitive data)
   - 21-40: Low-Medium (minor info)
   - 41-60: Medium (some credentials)
   - 61-80: High (clear credentials/PII)
   - 81-100: Critical (active credentials, database dumps, mass exposure)

2. SUMMARY (1-2 sentences): What was leaked?

3. RATIONALE: Why this score? What makes it dangerous?

4. ALERT LEVEL: LOW, MEDIUM, HIGH, or CRITICAL

5. SIGNALS (list): detected patterns like: passwords, api_keys, database_credentials, admin_access, pii, credit_cards, ssh_keys, tokens, emails, phone_numbers

6. MITIGATION RECOMMENDATIONS (detailed):
   - Immediate actions (0-24 hours)
   - Short-term fixes (1-7 days)
   - Long-term prevention
   - Specific technical steps
   - Who should be notified

Format your response EXACTLY like this:
SCORE: [number]
SUMMARY: [text]
RATIONALE: [text]
ALERT: [level]
SIGNALS: [comma,separated,list]
MITIGATION: [detailed recommendations with bullet points]"""

        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000,
            )
        )
        
        result_text = response.text
        
        # Parse response
        score = 0.0
        summary = "Analysis completed"
        rationale = ""
        alert = "LOW"
        signals = []
        mitigation = ""
        
        for line in result_text.split('\n'):
            line = line.strip()
            if line.startswith('SCORE:'):
                try:
                    score = float(line.split(':', 1)[1].strip())
                except:
                    score = 50.0
            elif line.startswith('SUMMARY:'):
                summary = line.split(':', 1)[1].strip()
            elif line.startswith('RATIONALE:'):
                rationale = line.split(':', 1)[1].strip()
            elif line.startswith('ALERT:'):
                alert = line.split(':', 1)[1].strip().upper()
            elif line.startswith('SIGNALS:'):
                signals_str = line.split(':', 1)[1].strip()
                signals = [s.strip() for s in signals_str.split(',') if s.strip()]
            elif line.startswith('MITIGATION:'):
                mitigation = line.split(':', 1)[1].strip()
                # Capture multi-line mitigation
                mitigation_lines = [mitigation]
                remaining = result_text.split('MITIGATION:', 1)[1].strip()
                if remaining:
                    mitigation = remaining
        
        return {
            "index": index,
            "vulnerability_score": min(100.0, max(0.0, score)),
            "summary": summary[:500],
            "rationale": rationale[:800],
            "alerts": alert if alert in ["LOW", "MEDIUM", "HIGH", "CRITICAL"] else "MEDIUM",
            "signals": signals,
            "mitigation": mitigation[:2000]  # Limit but allow longer text
        }
        
    except Exception as e:
        logger.error(f"Gemini analysis error for item {index}: {e}")
        return {
            "index": index,
            "vulnerability_score": 0.0,
            "summary": "Analysis failed",
            "rationale": f"Error during AI analysis: {str(e)[:200]}",
            "alerts": "LOW",
            "signals": [],
            "mitigation": "Unable to generate mitigation recommendations due to analysis failure."
        }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Nexzy AI Scoring Service",
        "status": "online",
        "gemini_configured": bool(GEMINI_API_KEY),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "gemini_api": "configured" if GEMINI_API_KEY else "not_configured",
        "model": "gemini-2.0-flash-exp",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/analyze_batch", response_model=Dict)
async def analyze_batch(request: AnalyzeRequest):
    """
    Analyze multiple text items in parallel
    Returns vulnerability scores, summaries, and mitigation recommendations
    """
    logger.info(f"📥 Received batch analysis request: {len(request.items)} items")
    
    if not request.items:
        return {"results": []}
    
    # Limit concurrent Gemini calls
    semaphore = asyncio.Semaphore(request.max_parallel_gemini)
    
    async def analyze_with_limit(item_dict: Dict, idx: int):
        async with semaphore:
            return await analyze_with_gemini(
                text=item_dict.get("text", ""),
                url=item_dict.get("url"),
                index=idx
            )
    
    # Run analyses in parallel
    tasks = [
        analyze_with_limit(item, i)
        for i, item in enumerate(request.items)
    ]
    
    results = await asyncio.gather(*tasks)
    
    logger.info(f"✅ Completed {len(results)} analyses")
    
    return {"results": results}

@app.post("/analyze_single")
async def analyze_single(text: str, url: Optional[str] = None):
    """Analyze a single text item"""
    result = await analyze_with_gemini(text, url, 0)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
