# 🤖 AI Integration Guide - Nexzy + AI-Scoring-and-Summarizing

## 📋 Overview

This guide explains how to integrate the **AI-Scoring-and-Summarizing_NEXT** module into Nexzy for intelligent threat analysis.

### What the AI Module Does:
1. **Risk Scoring (0-100)** - XLM-RoBERTa model predicts vulnerability score
2. **PII Masking** - Automatically masks emails, phones, IDs before analysis
3. **AI Summarization** - Gemini LLM generates concise summaries + risk rationale
4. **Batch Processing** - Handles multiple texts efficiently

---

## 🏗️ Architecture

```
User creates scan
  ↓
Nexzy Backend: Scrape paste sites
  ↓
Nexzy Backend: Extract credentials
  ↓
>>> NEW: Call AI Service via HTTP <<<
  ↓
AI Service: Score + Summarize + Mask PII
  ↓
Nexzy Backend: Create enriched alerts
  ↓
Frontend: Display AI-powered insights
```

---

## 🚀 Step 1: Setup AI Service (Separate Microservice)

### 1.1 Clone the AI Repository

```bash
cd C:\Users\calvi\Desktop\Study\nexzy
git clone https://github.com/Haraafu/AI-Scoring-and-Summarizing_NEXT ai-service
cd ai-service
```

### 1.2 Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 1.3 Setup Environment Variables

Create `.env` file:

```env
# AI Service Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_DIR=models/roberta-risk
MODEL_NAME=xlm-roberta-base
ALERT_HIGH=80
ALERT_MED=50
PORT=8081
```

**Get Gemini API Key:**
1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy to `.env`

### 1.4 Prepare the Model

**Option A: Download Pre-trained Model** (if available)

```bash
# Download from Hugging Face
python src/download_model.py
```

**Option B: Train from Scratch**

Create training data `data/train.csv`:

```csv
text,score
"Email: john@corp.com password: test123",85
"Public document with no PII",15
"Customer list with phone numbers: 08123456789",70
"General article about security",10
```

Create validation data `data/valid.csv` (same format, different samples)

Then train:

```bash
python src/train_regression.py
```

Model will be saved to `models/roberta-risk/`

### 1.5 Test the Model

```bash
python src/check_inference.py
```

Expected output:
```
[85.23] Email karyawan john@corp.co dan password disebutkan di forum
[12.45] Dokumen umum tanpa PII
[68.90] Daftar pelanggan lengkap dengan nomor HP
[9.12] Artikel umum tentang keamanan data
```

### 1.6 Start AI Service

```powershell
uvicorn src.service_batch:app --host 0.0.0.0 --port 8081 --reload
```

Service running at: http://localhost:8081

**Test endpoint:**
```bash
curl -X POST http://localhost:8081/analyze_batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"text": "Email: test@ui.ac.id password: 123456"}],
    "score_threshold": 40
  }'
```

---

## 🔗 Step 2: Connect Nexzy Backend to AI Service

### 2.1 Install Dependencies

```bash
cd C:\Users\calvi\Desktop\Study\nexzy\nexzy-backend
.\venv\Scripts\Activate.ps1
pip install httpx
```

### 2.2 AI Client Already Created

File `lib/ai_client.py` sudah dibuat dengan functions:
- `analyze_batch()` - Batch analysis
- `score_single_text()` - Single text scoring

### 2.3 Update Backend Configuration

Update `config.py`:

```python
# AI Service Configuration
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8081")
AI_SCORE_THRESHOLD = float(os.getenv("AI_SCORE_THRESHOLD", "40.0"))
```

Update `.env`:

```env
# Existing vars...
AI_SERVICE_URL=http://localhost:8081
AI_SCORE_THRESHOLD=40.0
```

### 2.4 Integration Already Done

File `api/main.py` sudah diupdate untuk:
1. Call AI service saat scan selesai
2. Enrich alerts dengan AI scores, summaries, rationale
3. Fallback gracefully kalo AI service down

---

## 📊 Step 3: Update Frontend to Display AI Insights

### 3.1 Update AlertDetails Component

```jsx
// src/pages/AlertDetails.jsx
// Add AI Score display in alert header
<div className="flex items-center gap-4">
  <div className="text-5xl font-bold text-white">
    {alert.ai_score || alert.severity_score}
    <span className="text-grey text-2xl">/100</span>
  </div>
  {alert.ai_score && (
    <div className="text-xs text-grey">
      <div>AI Risk Score</div>
      <div className="text-skyblue">{alert.ai_alert_level}</div>
    </div>
  )}
</div>

// Add AI Summary section
{alert.ai_summary && (
  <div className="glass-panel p-6 rounded-xl border border-white/10">
    <h3 className="text-white font-bold mb-3">🤖 AI Summary</h3>
    <p className="text-grey leading-relaxed">{alert.ai_summary}</p>
  </div>
)}

// Add Risk Rationale section
{alert.ai_rationale && (
  <div className="glass-panel p-6 rounded-xl border border-orange/10">
    <h3 className="text-orange font-bold mb-3">⚠️ Risk Assessment</h3>
    <p className="text-grey leading-relaxed">{alert.ai_rationale}</p>
  </div>
)}

// Add Detected Signals section
{alert.ai_signals && alert.ai_signals.length > 0 && (
  <div className="glass-panel p-6 rounded-xl border border-white/10">
    <h3 className="text-white font-bold mb-3">🔍 Detected Signals</h3>
    <div className="flex flex-wrap gap-2">
      {alert.ai_signals.map((signal, idx) => (
        <span key={idx} className="px-3 py-1 bg-red/10 text-red rounded border border-red/20 text-xs">
          {signal}
        </span>
      ))}
    </div>
  </div>
)}
```

### 3.2 Update Dashboard Stats

Show AI-powered stats:

```jsx
// src/pages/Dashboard.jsx
const [aiStats, setAiStats] = useState({
  avgRiskScore: 0,
  highRiskCount: 0,
  criticalSignals: 0
});

// Calculate from alerts
useEffect(() => {
  if (alerts.length > 0) {
    const scores = alerts.map(a => a.ai_score || 0).filter(s => s > 0);
    const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
    const highRisk = alerts.filter(a => (a.ai_score || 0) >= 70).length;
    const criticalSignals = alerts.filter(a => 
      a.ai_signals && a.ai_signals.includes('email')
    ).length;
    
    setAiStats({ avgRiskScore: avgScore, highRiskCount: highRisk, criticalSignals });
  }
}, [alerts]);

// Display AI stats cards
<StatsCard
  title="Avg Risk Score"
  value={aiStats.avgRiskScore.toFixed(1)}
  color="orange"
  icon="🤖"
/>
```

---

## 🧪 Step 4: Testing the Integration

### 4.1 End-to-End Test

1. **Start all services:**

```powershell
# Terminal 1: AI Service
cd ai-service
.\venv\Scripts\Activate.ps1
uvicorn src.service_batch:app --host 0.0.0.0 --port 8081

# Terminal 2: Nexzy Backend
cd nexzy-backend
.\venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Terminal 3: Nexzy Frontend
cd nexzy-frontend
npm run dev
```

2. **Create a test scan:**
   - Login to Nexzy
   - Create new scan with Pastebin URL
   - Wait for scan completion
   - Check alert details for AI insights

3. **Verify AI data:**
   - Alert should show "AI Score: XX/100" in title
   - Description should contain AI Summary and Risk Assessment
   - Detected signals should be listed

### 4.2 Manual API Test

```bash
# Test AI service directly
curl -X POST http://localhost:8081/analyze_batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "text": "npm: 2006596371\nNama: John Doe\nEmail: john@ui.ac.id\nNo. HP: 08123456789",
        "url": "https://pastebin.com/test123",
        "timestamp": "2025-12-01T10:00:00Z"
      }
    ],
    "score_threshold": 30,
    "max_parallel_gemini": 4
  }'
```

Expected response:
```json
{
  "results": [
    {
      "index": 0,
      "vulnerability_score": 78.5,
      "summary": "Student data leak containing NPM, name, email, and phone number",
      "rationale": "High risk due to multiple PII fields including student ID and contact information",
      "alerts": "HIGH",
      "signals": ["email", "phone_candidate", "id_candidate"]
    }
  ]
}
```

---

## 🚀 Step 5: Production Deployment

### 5.1 Deploy AI Service

**Option A: Google Cloud Run**

```bash
# Build and deploy
gcloud run deploy nexzy-ai-service \
  --source . \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=xxx
```

**Option B: Railway**

1. Push to GitHub
2. Create new Railway project
3. Connect GitHub repo (ai-service folder)
4. Set environment variables
5. Deploy

**Option C: VPS/Docker**

```bash
# Build Docker image
docker build -t nexzy-ai-service .

# Run container
docker run -d -p 8081:8080 \
  -e GEMINI_API_KEY=xxx \
  --name nexzy-ai \
  nexzy-ai-service
```

### 5.2 Update Nexzy Backend .env

```env
AI_SERVICE_URL=https://your-ai-service.run.app
```

### 5.3 Monitor Performance

AI service logs show:
- Request count
- Average processing time
- Error rates
- Gemini API quota usage

---

## 📈 Benefits of Integration

| Feature | Before | After (with AI) |
|---------|--------|-----------------|
| **Risk Scoring** | Heuristic (target email count) | ML-powered 0-100 score |
| **Severity** | Manual rules | AI-determined HIGH/MEDIUM/LOW |
| **Context** | Raw paste content | Masked PII + concise summary |
| **Rationale** | None | Detailed risk explanation |
| **Signals** | Basic regex | Advanced PII detection |
| **Language** | English only | Multi-language support (XLM-RoBERTa) |

---

## 🔧 Troubleshooting

### AI Service Not Responding

**Check:**
1. Is service running? `curl http://localhost:8081/docs`
2. Check logs for errors
3. Verify Gemini API key is valid
4. Check model files exist in `models/roberta-risk/`

**Solution:**
```bash
# Restart service
uvicorn src.service_batch:app --host 0.0.0.0 --port 8081 --reload
```

### Model Not Found Error

```
FileNotFoundError: models/roberta-risk
```

**Solution:**
Train or download model first:
```bash
python src/train_regression.py
```

### Gemini API Quota Exceeded

**Error:** "429 Resource Exhausted"

**Solution:**
1. Reduce `max_parallel_gemini` to 4-8
2. Increase `score_threshold` to 50-70 (fewer calls)
3. Upgrade Gemini API plan

### High Memory Usage

**Problem:** AI service using >2GB RAM

**Solution:**
- Use smaller model: `MODEL_NAME=distilbert-base-multilingual-cased`
- Reduce batch size: `batch_size=16`
- Deploy to higher-tier instance

---

## 🎯 Next Steps

1. **Fine-tune Model** on your specific domain (ui.ac.id leaks)
2. **Add Caching** - Cache AI results for duplicate content
3. **A/B Testing** - Compare AI vs heuristic severity
4. **Feedback Loop** - Let users rate AI summaries, retrain model
5. **Multi-Model** - Add specialized models (credential extraction, language detection)

---

## 📚 References

- **AI Repo:** https://github.com/Haraafu/AI-Scoring-and-Summarizing_NEXT
- **XLM-RoBERTa:** https://huggingface.co/docs/transformers/model_doc/xlm-roberta
- **Gemini API:** https://ai.google.dev/gemini-api/docs
- **LangChain:** https://python.langchain.com/docs/get_started/introduction

---

## ✅ Integration Checklist

- [ ] Clone AI-Scoring-and-Summarizing_NEXT repo
- [ ] Setup virtual environment and install dependencies
- [ ] Configure Gemini API key
- [ ] Train or download model
- [ ] Start AI service on port 8081
- [ ] Test AI service endpoint
- [ ] Install httpx in Nexzy backend
- [ ] Update Nexzy backend config
- [ ] Test integration (create scan with credentials)
- [ ] Verify AI data in alert details
- [ ] Update frontend to display AI insights
- [ ] Deploy AI service to production
- [ ] Update production env vars
- [ ] Monitor performance and errors

**Status:** ✅ Backend integration complete, Frontend updates pending
