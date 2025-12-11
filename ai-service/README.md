# 🚀 START AI SERVICE NOW!

## You need a Gemini API key (takes 30 seconds, FREE!)

### Step 1: Get API Key

Go to: **https://aistudio.google.com/app/apikey**
- Click "Create API Key"
- Copy the key (starts with `AIza...`)

### Step 2: Add to .env

Open `ai-service/.env` and paste your key:

```env
GEMINI_API_KEY=AIzaSyC...your_key_here
```

### Step 3: Start AI Service

Open a NEW terminal and run:

```powershell
cd "c:\Users\calvi\Documents\My Projects\nexzy\ai-service"
.\start.ps1
```

This will start the AI service on **port 8001**.

### What You Get

✅ **AI Vulnerability Scoring (0-100)**  
✅ **Risk Summaries & Rationale**  
✅ **Threat Signal Detection**  
✅ **🛡️ MITIGATION RECOMMENDATIONS** ← NEW!

Example mitigation output:

```
🛡️ MITIGATION RECOMMENDATIONS:

IMMEDIATE (0-24 hours):
• Force password reset for all exposed accounts
• Disable compromised admin accounts  
• Contact pastebin.com for content removal
• Alert affected students via email

SHORT-TERM (1-7 days):
• Audit database access logs
• Implement password hashing (bcrypt)
• Enable 2FA for all accounts
• Review security configurations

LONG-TERM:
• Automated credential leak monitoring
• Regular security training
• Database encryption at rest
• Incident response procedures

NOTIFY:
• University IT Security Team
• Data Protection Officer
• Affected students
• Cyber authorities
```

### Testing

After starting AI service:

1. Go to http://localhost:5174
2. Start a new scan
3. Wait for credentials to be detected
4. Open alert details
5. See **Mitigation Recommendations** section!

### Cost

- **100% FREE** for normal usage
- Gemini 2.0 Flash: 15 requests/min free
- 1 million tokens/day free
- No credit card required

---

**Backend is already configured** - just start AI service!

AI_SERVICE_URL=http://localhost:8001 ✅
