# ⚠️ AI Service Unavailable - Fix Guide

## Problem
You're seeing "AI service unavailable" errors in scan logs.

## Root Cause
**AI_SERVICE_URL** is configured to `http://localhost:8000` in config.py, which conflicts with Nexzy backend's own port (also 8000). The AI service is a **separate service** for vulnerability scoring and summarization using Gemini AI.

## Quick Fix ✅ (System Works Without AI)

The system already has graceful fallback - it works perfectly fine **without** AI service! 

**What you get without AI:**
- ✅ Credential detection still works
- ✅ Email extraction still works
- ✅ Relevance scoring still works
- ✅ Alerts still created
- ❌ No AI vulnerability scores (0.0)
- ❌ No AI-generated summaries
- ❌ No AI rationales

**To explicitly disable AI service:**

1. Open `.env` file
2. Set `AI_SERVICE_URL` to empty:
   ```env
   AI_SERVICE_URL=
   ```
3. Restart backend
4. Logs will show: "AI service disabled (AI_SERVICE_URL not configured)"

## Complete Fix (If You Want AI Features)

The AI service is a separate Python service that uses Google Gemini API for advanced analysis.

### Option 1: Use Existing AI Service (If You Have It)

If you already have the AI scoring service running:

1. **Find AI service port** (usually 8001 or different from 8000)
2. **Update `.env`:**
   ```env
   AI_SERVICE_URL=http://localhost:8001
   ```
3. **Restart backend**

### Option 2: Set Up AI Service (Advanced)

If you want AI features, you need to:

1. **Get the AI service code** (separate repo/service)
2. **Install dependencies:**
   ```bash
   pip install google-generativeai
   ```
3. **Configure Gemini API key**
4. **Run AI service on different port:**
   ```bash
   uvicorn ai_service:app --port 8001
   ```
5. **Update `.env`:**
   ```env
   AI_SERVICE_URL=http://localhost:8001
   ```

### Option 3: Disable AI Service (Recommended for Now)

If you don't have the AI service and don't need it:

1. **Edit `.env`:**
   ```env
   # Disable AI service
   AI_SERVICE_URL=
   ```
2. **Restart backend**
3. **System works normally without AI scores**

## What AI Service Does

When enabled, AI service provides:

1. **Vulnerability Scoring (0-100)**
   - Analyzes content for security risks
   - Detects credential patterns
   - Identifies PII exposure
   - Scores threat level

2. **AI Summaries**
   - One-sentence summary of the leak
   - Context about what was exposed
   - Impact assessment

3. **Risk Rationale**
   - Explanation of why score is high/low
   - Detected signals (passwords, emails, API keys, etc.)
   - Alert level (LOW/MEDIUM/HIGH)

## Impact on Alerts

**With AI Service:**
```
Alert Title: Data Leak Detected - pastebin.com (AI Score: 85)
Severity: CRITICAL (based on AI score 85)
Description: Contains exposed credentials...

AI Summary: Database dump containing 50+ passwords and admin credentials.
Risk Assessment: High risk due to plaintext passwords and privileged access.
Detected Signals: passwords, database_credentials, admin_access
Vulnerability Score: 85/100
```

**Without AI Service:**
```
Alert Title: Data Leak Detected - pastebin.com
Severity: HIGH (based on heuristic: 5+ target emails found)
Description: Contains exposed credentials...

[No AI summary]
[No AI rationale]
[No AI signals]
```

Both work! AI just adds more detailed analysis.

## Current Status After Fix

✅ **Backend running:** Port 8000  
✅ **AI_SERVICE_URL:** Empty (disabled)  
✅ **System status:** Fully functional  
✅ **Scan detection:** Working (heuristic-based)  
❌ **AI features:** Disabled (no Gemini analysis)

## Verification

Check backend logs after restart:

**With AI disabled (correct):**
```
INFO:lib.ai_client:AI service disabled (AI_SERVICE_URL not configured)
INFO:__main__:[ALERTS] Creating alerts for 3 credential leaks...
INFO:__main__:[OK] Alert created: HIGH - Data Leak Detected
```

**With AI enabled and working:**
```
INFO:__main__:[AI] Preparing 3 items for AI analysis...
INFO:__main__:[AI] Received 3 AI analysis results
INFO:__main__:[OK] Alert created: CRITICAL - AI Score: 85
```

**With AI enabled but unavailable (error):**
```
ERROR:lib.ai_client:AI service error: ConnectError
ERROR:__main__:[AI] Analysis failed: ...
INFO:__main__:[OK] Alert created: HIGH - Data Leak Detected
```

## Recommendation

**For now:** Keep AI service **disabled** (AI_SERVICE_URL empty)

**Reasons:**
1. System works perfectly without it
2. No dependency on external AI service
3. Faster scans (no AI API calls)
4. No Gemini API costs
5. Simpler setup

**When to enable AI:**
1. You have Gemini API key
2. You want AI-powered vulnerability scoring
3. You want AI-generated summaries
4. You deploy the AI service separately

---

**Current Config:** ✅ AI Disabled, System Working  
**Action Required:** None - restart backend to apply  
**System Impact:** None - fully functional
