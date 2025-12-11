# 🤖 AI Scoring Service - Setup & Usage Guide

## What You Just Got

**Complete AI-powered vulnerability analysis with mitigation recommendations!**

Your new AI service provides:
- ✅ **Vulnerability Scoring (0-100)** - Automated risk assessment
- ✅ **AI Summaries** - One-sentence leak descriptions
- ✅ **Risk Rationale** - Detailed explanations of threats
- ✅ **Signal Detection** - Identifies passwords, API keys, PII, etc.
- ✅ **Mitigation Recommendations** - Actionable steps to fix the issue

## 🚀 Quick Start

### 1. Install AI Service Dependencies

```powershell
cd "c:\Users\calvi\Documents\My Projects\nexzy\ai-service"
pip install -r requirements.txt
```

### 2. Get Google Gemini API Key (FREE!)

1. Go to: **https://aistudio.google.com/app/apikey**
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### 3. Configure API Key

```powershell
# Create .env file
Copy-Item .env.example .env

# Edit .env and add your key:
# GEMINI_API_KEY=AIzaSyC...your_key_here
```

Or edit `.env` manually in VS Code.

### 4. Start AI Service

**Terminal 1** - AI Service (Port 8001):
```powershell
cd "c:\Users\calvi\Documents\My Projects\nexzy\ai-service"
.\start.ps1
```

**Terminal 2** - Nexzy Backend (Port 8000):
```powershell
cd "c:\Users\calvi\Documents\My Projects\nexzy\nexzy-backend"
.\start.ps1
```

**Terminal 3** - Frontend (Port 5174):
```powershell
cd "c:\Users\calvi\Documents\My Projects\nexzy\nexzy-frontend"
npm run dev
```

### 5. Test It!

1. Go to **http://localhost:5174**
2. Click **"NEW SCAN"**
3. Start a scan with credentials
4. Watch AI analyze each leak in real-time!
5. Open alert details to see **Mitigation Recommendations** section

## 📋 What AI Service Does

### Before (No AI):
```
Alert Title: Data Leak Detected - pastebin.com
Severity: HIGH (heuristic: 5+ emails)
Description: Contains exposed credentials...
```

### After (With AI):
```
Alert Title: Data Leak Detected - pastebin.com (AI Score: 87)
Severity: CRITICAL (AI-powered)
Description: Contains exposed credentials...

AI Summary: Database dump containing 50+ student passwords and admin credentials.

Risk Assessment: High severity due to plaintext passwords with university 
email domains. Appears to be from compromised student database.

Detected Signals: passwords, database_credentials, admin_access, emails, pii

🛡️ MITIGATION RECOMMENDATIONS:
IMMEDIATE (0-24 hours):
• Force password reset for all exposed accounts
• Disable compromised admin accounts
• Contact pastebin.com for content removal
• Alert affected students via email

SHORT-TERM (1-7 days):
• Audit database access logs for breach point
• Implement password hashing (bcrypt/argon2)
• Enable 2FA for all university accounts
• Review database security configurations

LONG-TERM:
• Implement automated credential leak monitoring
• Regular security training for IT staff
• Deploy database encryption at rest
• Establish incident response procedures

NOTIFY:
• University IT Security Team (urgent)
• Data Protection Officer
• Affected students (after mitigation)
• Local cyber authorities (if required by law)

Source URL: https://pastebin.com/abc123
Vulnerability Score: 87.0/100
```

## 🎯 AI Analysis Flow

```
User starts scan
    ↓
Backend finds credentials
    ↓
Sends to AI Service (port 8001)
    ↓
AI Service → Gemini API
    ↓
Gemini analyzes content:
  - Reads paste text
  - Identifies threats
  - Scores severity (0-100)
  - Generates mitigation steps
    ↓
AI Service returns results
    ↓
Backend creates alerts with AI data
    ↓
Frontend displays recommendations
```

## 🔧 Configuration Files

### `.env` (AI Service)
```env
GEMINI_API_KEY=AIzaSyC...your_key_here
```

### `.env` (Backend)
```env
AI_SERVICE_URL=http://localhost:8001
```

## 🧪 Testing

### Check AI Service Health
```powershell
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "gemini_api": "configured",
  "model": "gemini-2.0-flash-exp",
  "timestamp": "2025-12-11T..."
}
```

### Test Single Analysis
```powershell
curl -X POST http://localhost:8001/analyze_single `
  -H "Content-Type: application/json" `
  -d '{"text": "password: admin123 email: test@ui.ac.id", "url": "test"}'
```

## 💰 Pricing

**Google Gemini 2.0 Flash:**
- ✅ **FREE tier**: 15 requests/minute
- ✅ **FREE tier**: 1 million tokens/day
- ✅ **No credit card required** for testing

For Nexzy usage:
- ~1-10 requests per scan (only items with credentials)
- ~500-2000 tokens per analysis
- **FREE for thousands of scans per day!**

## 🐛 Troubleshooting

### "AI service unavailable"
- Check AI service is running on port 8001
- Check `AI_SERVICE_URL=http://localhost:8001` in backend .env
- Restart backend after changing .env

### "Mock Analysis" in results
- GEMINI_API_KEY not set
- Check `.env` file in ai-service folder
- Key should start with `AIza...`

### "Analysis failed"
- Check Gemini API quota (15 req/min free)
- Check internet connection
- Check API key is valid

## 📂 File Structure

```
ai-service/
  main.py           # FastAPI service
  requirements.txt  # Dependencies
  .env             # Your API key (create this)
  .env.example     # Template
  start.ps1        # Startup script
```

## 🎨 Frontend Integration

Mitigation recommendations automatically appear in:
- **Alert Details page** - Green bordered section
- **Alert descriptions** - Formatted with sections
- **Alerts list** - Included in descriptions

## ⚡ Performance

- **Parallel Processing**: Analyzes 8-16 items concurrently
- **Smart Caching**: Reuses Gemini sessions
- **Rate Limiting**: Respects API limits automatically
- **Timeout**: 120 seconds per batch

## 🔐 Security

- API key stored in `.env` (not in code)
- HTTPS communication with Gemini
- CORS enabled for localhost only
- No data retention (stateless service)

## 🚀 Production Deployment

For production:
1. Deploy AI service to cloud (Heroku, Railway, etc.)
2. Update `AI_SERVICE_URL` in backend .env
3. Use environment variables for API key
4. Consider paid Gemini tier for higher limits

## 📖 API Documentation

Once running, visit:
- **http://localhost:8001/docs** - Swagger UI
- **http://localhost:8001/redoc** - ReDoc

---

**Status:** ✅ AI Service Ready  
**Next Step:** Get Gemini API key and start the service!  
**Cost:** 🆓 FREE Forever (with reasonable usage)
