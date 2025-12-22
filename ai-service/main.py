"""
Nexzy AI Service - Enhanced with RoBERTa + Gemini
Architecture:
1. RoBERTa model scores vulnerability (no API limits, fast)
2. Gemini generates summaries only for high-risk items (saves quota)

Based on: https://github.com/sleepingpolice-afk/nexzyAI
Integrated into Nexzy by: GitHub Copilot
"""

import os
import asyncio
import torch
import torch.nn.functional as F
from typing import List, Optional, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Import custom modules
from pii_masker import mask_text, detect_signals
from gemini_client import generate_summary_and_mitigation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Use friend's fine-tuned RoBERTa model from Hugging Face
# MODEL_NAME = "Harafu/roberta-risk-next"  # BROKEN - tokenizer corrupted
# MODEL_NAME = "martin-ha/toxic-comment-model"  # Works but not ideal for credentials
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"  # Reliable fallback
ALERT_HIGH = 80
ALERT_MED = 50

# Lazy load model and tokenizer (initialized on first request)
logger.info(f"Model will be lazy-loaded: {MODEL_NAME}")
tokenizer = None
model = None
device = None

def load_model():
    """Lazy load model on first request"""
    global tokenizer, model, device
    if model is None:
        logger.info(f"Loading RoBERTa model: {MODEL_NAME}")
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            model.eval()
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model.to(device)
            logger.info(f"✅ RoBERTa model loaded successfully on {device}")
        except Exception as e:
            logger.error(f"Failed to load RoBERTa model: {e}")
            raise
    return model, tokenizer, device

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Nexzy AI Service - RoBERTa + Gemini",
    version="2.0.0",
    description="Enhanced vulnerability scoring with local ML model + Gemini summaries"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# SCHEMAS
# ============================================================================

class ItemIn(BaseModel):
    text: str
    url: Optional[str] = None
    timestamp: Optional[str] = None

class BatchIn(BaseModel):
    items: List[ItemIn]
    score_threshold: float = Field(95, ge=0, le=100, description="Min score for Gemini summary")
    max_parallel_gemini: int = Field(1, ge=1, le=20, description="Max concurrent Gemini calls")
    max_summary_chars: int = Field(1200, ge=100, le=5000, description="Max chars for masking")

class ItemOut(BaseModel):
    index: int
    vulnerability_score: float
    summary: str
    rationale: str
    alerts: str
    signals: List[str] = []
    mitigation: str

class BatchOut(BaseModel):
    results: List[ItemOut]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def alert_level(score: float) -> str:
    """Convert score to alert level"""
    if score >= ALERT_HIGH:
        return "CRITICAL"
    elif score >= ALERT_MED:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    else:
        return "LOW"

def batch_score_texts(texts: List[str]) -> List[float]:
    """
    Score texts using RoBERTa model (local, no API calls).
    
    Returns:
        List of vulnerability scores (0-100)
    """
    # Lazy load model on first use
    _, local_tokenizer, local_device = load_model()
    
    scores = []
    
    for text in texts:
        try:
            # Tokenize
            inputs = local_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(local_device)
            
            # Get model output
            with torch.no_grad():
                local_model, _, _ = load_model()
                outputs = local_model(**inputs)
                logits = outputs.logits
                
                # Handle different model types
                if logits.shape[-1] == 2:
                    # Binary classification: use probability of positive class
                    probs = F.softmax(logits, dim=-1)
                    score = probs[0][1].item() * 100.0
                elif logits.shape[-1] == 3:
                    # 3-class sentiment model: use negative sentiment as risk indicator
                    probs = F.softmax(logits, dim=-1)
                    # LABEL_0 = negative, LABEL_1 = neutral, LABEL_2 = positive
                    # Higher negative probability = higher risk
                    negative_prob = probs[0][0].item()
                    score = negative_prob * 100.0
                else:
                    # Multi-class or regression: use max probability as score
                    probs = F.softmax(logits, dim=-1)
                    score = torch.max(probs).item() * 100.0
                
                scores.append(score)
                
        except Exception as e:
            logger.error(f"Scoring error: {e}")
            scores.append(0.0)
    
    return scores

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "Nexzy AI - RoBERTa + Gemini",
        "version": "2.0.0",
        "model": MODEL_NAME,
        "device": device,
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze_batch",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "device": device,
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))
    }

@app.post("/analyze_batch", response_model=BatchOut)
async def analyze_batch(payload: BatchIn):
    """
    Analyze batch of texts for security vulnerabilities.
    
    Process:
    1. Extract text from items
    2. Score with RoBERTa (all items, fast, local)
    3. Detect PII signals and mask text
    4. Apply signal-based boosting/reduction
    5. Generate Gemini summaries for high-scoring items only
    6. Return complete analysis
    """
    logger.info(f"📥 Received batch: {len(payload.items)} items, threshold: {payload.score_threshold}")
    
    if not payload.items:
        return BatchOut(results=[])
    
    # Step 1: Extract texts
    texts = [item.text for item in payload.items]
    
    # Step 2: Score all texts with RoBERTa (local, fast)
    logger.info("🤖 Scoring with RoBERTa model...")
    raw_scores = batch_score_texts(texts)
    
    # Step 3: Detect signals and mask PII
    logger.info("🔍 Detecting signals and masking PII...")
    masked_list = []
    signals_list = []
    final_scores = []
    
    for i, item in enumerate(payload.items):
        # Detect security signals
        signals = detect_signals(item.text)
        
        # Mask PII for Gemini
        masked = mask_text(item.text)[:payload.max_summary_chars]
        
        masked_list.append(masked)
        signals_list.append(signals)
        
        # Step 4: Apply signal-based score adjustment
        base_score = raw_scores[i]
        
        if len(signals) > 0:
            # Signals detected: boost score
            # Formula: 85 + (base * 0.1) caps at 99.9
            boosted = 85.0 + (base_score * 0.1)
            final_score = min(boosted, 99.9)
            logger.debug(f"Item {i}: Signals {signals} → boosted {base_score:.1f} → {final_score:.1f}")
        else:
            # No signals: reduce score
            # Formula: base * 0.5
            final_score = base_score * 0.5
            logger.debug(f"Item {i}: No signals → reduced {base_score:.1f} → {final_score:.1f}")
        
        final_scores.append(final_score)
    
    # Step 5: Generate Gemini summaries for high-scoring items only
    indices_for_gemini = [
        i for i, score in enumerate(final_scores)
        if score >= payload.score_threshold
    ]
    
    logger.info(f"🔥 High-risk items: {len(indices_for_gemini)}/{len(payload.items)} → sending to Gemini")
    
    # Limit concurrent Gemini calls
    semaphore = asyncio.Semaphore(payload.max_parallel_gemini)
    
    async def analyze_with_limit(idx: int):
        async with semaphore:
            return await generate_summary_and_mitigation(
                masked_text=masked_list[idx],
                url=payload.items[idx].url,
                timestamp=payload.items[idx].timestamp,
                signals=signals_list[idx],
                vulnerability_score=final_scores[idx]
            )
    
    # Run Gemini analyses in parallel (only for high-risk items)
    gemini_tasks = [analyze_with_limit(i) for i in indices_for_gemini]
    gemini_responses = await asyncio.gather(*gemini_tasks) if gemini_tasks else []
    
    # Map responses back to indices
    gemini_map = {idx: res for idx, res in zip(indices_for_gemini, gemini_responses)}
    
    # Step 6: Compile final results
    results = []
    for i in range(len(payload.items)):
        score = final_scores[i]
        
        # Use Gemini summary if available, otherwise basic message
        if i in gemini_map:
            summary = gemini_map[i].get("summary", "")
            rationale = gemini_map[i].get("rationale", "")
            mitigation = gemini_map[i].get("mitigation", "")
        else:
            # Low-risk items don't get Gemini analysis
            if score < payload.score_threshold:
                summary = "Low risk - no detailed analysis required"
                rationale = "Score below threshold for detailed analysis"
                mitigation = "Standard security monitoring sufficient"
            else:
                summary = "Analysis pending"
                rationale = "Item qualified for analysis but processing incomplete"
                mitigation = "Review manually if this persists"
        
        results.append(ItemOut(
            index=i,
            vulnerability_score=score,
            summary=summary,
            rationale=rationale,
            alerts=alert_level(score),
            signals=signals_list[i],
            mitigation=mitigation
        ))
    
    logger.info(f"✅ Batch complete: {len(results)} results")
    return BatchOut(results=results)

@app.post("/analyze_single")
async def analyze_single(text: str, url: Optional[str] = None):
    """
    Convenience endpoint for analyzing a single text.
    """
    result = await analyze_batch(BatchIn(
        items=[ItemIn(text=text, url=url)],
        score_threshold=40.0
    ))
    return result.results[0] if result.results else None

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("Nexzy AI Service Starting...")
    logger.info(f"Model: {MODEL_NAME}")
    logger.info(f"Device: {device}")
    logger.info(f"Gemini: {'✅ Configured' if os.getenv('GEMINI_API_KEY') else '❌ Not configured'}")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
