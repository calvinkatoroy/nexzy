"""
PII Detection and Masking Module
Detects sensitive information patterns and masks them for AI analysis
Based on: https://github.com/sleepingpolice-afk/nexzyAI
"""

import re
from typing import List

# Regex patterns for PII detection
EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b')
PHONE = re.compile(r'\b(\+?\d{1,3}[-.\s]?)?\d{8,14}\b')
IDNUM = re.compile(r'\b\d{8,16}\b')
PASS_HINT = re.compile(r'(?i)(password|passwd|pwd|kata\s*sandi|creds?|credentials)')

# Additional patterns
API_KEY = re.compile(r'(?i)(api[_-]?key|apikey|access[_-]?token|secret[_-]?key)[\s:=]+[\w-]{16,}')
CREDIT_CARD = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
IP_ADDRESS = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

def detect_signals(text: str) -> List[str]:
    """
    Detect security risk signals in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of detected signal types
    """
    signals = []
    
    if EMAIL.search(text): 
        signals.append("email")
    if PASS_HINT.search(text): 
        signals.append("password_hint")
    if IDNUM.search(text): 
        signals.append("id_candidate")
    if PHONE.search(text): 
        signals.append("phone_candidate")
    if API_KEY.search(text):
        signals.append("api_key")
    if CREDIT_CARD.search(text):
        signals.append("credit_card")
    if IP_ADDRESS.search(text):
        signals.append("ip_address")
        
    return signals

def mask_text(text: str) -> str:
    """
    Mask sensitive information in text.
    
    Args:
        text: Text to mask
        
    Returns:
        Masked text with PII replaced by placeholders
    """
    # Mask in order of specificity (most specific first)
    masked = API_KEY.sub("[API_KEY]", text)
    masked = CREDIT_CARD.sub("[CREDIT_CARD]", masked)
    masked = EMAIL.sub("[EMAIL]", masked)
    masked = PHONE.sub("[PHONE]", masked)
    masked = IDNUM.sub("[ID]", masked)
    masked = IP_ADDRESS.sub("[IP]", masked)
    
    return masked
