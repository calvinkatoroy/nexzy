"""
Gemini AI Client for Summary and Mitigation Generation
Adapted from: https://github.com/sleepingpolice-afk/nexzyAI
"""

import os
import json
import re
from typing import List, Optional, Dict
from dotenv import load_dotenv
import google.generativeai as genai
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def configure_gemini():
    """Configure Gemini API with safety settings disabled"""
    if not GEMINI_API_KEY:
        logger.warning("⚠️ GEMINI_API_KEY not set - summaries will be disabled")
        return None
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Configure safety settings to BLOCK_NONE for analyzing leaked data
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # Use gemini-2.5-flash-lite: 10 RPM / 20 RPD (best available in free tier)
        # Better than gemini-2.5-flash which only has 5 RPM
        model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            safety_settings=safety_settings
        )
        
        logger.info("✅ Gemini API configured with relaxed safety filters")
        return model
    except Exception as e:
        logger.error(f"Failed to configure Gemini: {e}")
        return None

# Initialize model at module load
gemini_model = configure_gemini()

def clean_and_parse_json(text_output: str) -> Dict:
    """
    Extract and parse JSON from Gemini response.
    Handles markdown code blocks and malformed responses.
    """
    text_output = text_output.strip()
    
    # Remove Markdown code blocks if present
    if "```" in text_output:
        pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        match = re.search(pattern, text_output, re.DOTALL)
        if match:
            text_output = match.group(1)
    
    # Try to parse JSON
    try:
        return json.loads(text_output)
    except json.JSONDecodeError:
        # Fallback: extract JSON object with regex
        match = re.search(r"\{.*\}", text_output, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except:
                pass
    
    # Check if blocked by safety filters
    if not text_output.strip():
        return {
            "summary": "Content blocked by safety filters",
            "rationale": "Gemini safety filters blocked this content analysis.",
            "mitigation": "Manual review required due to content sensitivity."
        }
    
    # Last resort: return raw text
    return {
        "summary": text_output[:300] if text_output else "Analysis unavailable",
        "rationale": "Failed to parse structured response",
        "mitigation": "Manual analysis recommended"
    }

async def generate_summary_and_mitigation(
    masked_text: str,
    url: Optional[str],
    timestamp: Optional[str],
    signals: List[str],
    vulnerability_score: float
) -> Dict:
    """
    Generate summary, rationale, and mitigation recommendations using Gemini.
    
    Args:
        masked_text: Text with PII masked
        url: Source URL
        timestamp: Discovery timestamp
        signals: List of detected security signals
        vulnerability_score: Risk score from RoBERTa model
        
    Returns:
        Dict with summary, rationale, and mitigation fields
    """
    if not gemini_model:
        return {
            "summary": "Gemini API unavailable",
            "rationale": "GEMINI_API_KEY not configured",
            "mitigation": "Configure GEMINI_API_KEY for AI-generated recommendations"
        }
    
    try:
        # DEBUG: Log Gemini call
        logger.info(f"🔵 Calling Gemini API for score {vulnerability_score:.1f} with signals: {signals}")
        
        # Build prompt
        signals_str = ", ".join(signals) if signals else "None detected"
        
        prompt = f"""You are a cybersecurity analyst. Analyze this data leak and provide recommendations.

**Context:**
- URL: {url or 'Unknown'}
- Timestamp: {timestamp or 'Unknown'}
- Risk Score: {vulnerability_score:.1f}/100
- Detected Signals: {signals_str}

**Content (PII masked):**
{masked_text[:2000]}

**Instructions:**
1. Write a concise summary (1-2 sentences) of what was leaked
2. Explain the rationale for the risk level based on detected signals
3. Provide actionable mitigation recommendations
4. Use the same language as the content (English/Indonesian)
5. Do NOT try to unmask or guess redacted PII

**Output Format (JSON only, no markdown):**
{{
  "summary": "Brief description of the leak",
  "rationale": "Why this is high/medium/low risk",
  "mitigation": "Step-by-step mitigation actions"
}}"""

        # Generate response
        response = await gemini_model.generate_content_async(prompt)
        
        if not response or not response.text:
            raise ValueError("Empty response from Gemini")
        
        # Parse response
        result = clean_and_parse_json(response.text)
        
        # DEBUG: Log success
        logger.info(f"✅ Gemini API call successful for score {vulnerability_score:.1f}")
        
        # Ensure all required fields exist and are strings (not lists)
        def to_string(value, default):
            if isinstance(value, list):
                return "\n".join(str(item) for item in value)
            elif value:
                return str(value)
            return default
        
        return {
            "summary": to_string(result.get("summary"), "Analysis completed"),
            "rationale": to_string(result.get("rationale"), "Based on detected patterns and signals"),
            "mitigation": to_string(result.get("mitigation"), "Review and secure exposed data immediately")
        }
        
    except Exception as e:
        # Check if it's a rate limit error
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            logger.warning(f"⚠️ RATE LIMITED: {error_str[:200]}")
        else:
            logger.error(f"❌ Gemini generation error: {e}")
        return {
            "summary": "Analysis failed",
            "rationale": f"Error: {str(e)[:200]}",
            "mitigation": "Manual review required. Check AI service logs for details."
        }
