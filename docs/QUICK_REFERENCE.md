# 🚀 Quick Reference - Nexzy Commands

## Starting Services

### All Services (Recommended Order)

```powershell
# Terminal 1 - Backend
cd "c:\Users\calvi\Documents\My Projects\nexzy\nexzy-backend"
.\start.ps1

# Terminal 2 - Frontend  
cd "c:\Users\calvi\Documents\My Projects\nexzy\nexzy-frontend"
npm run dev

# Terminal 3 - AI Service (Optional)
cd "c:\Users\calvi\Documents\My Projects\nexzy\ai-service"
.\start.ps1
```

### Manual Start Commands

**Backend:**
```powershell
cd nexzy-backend
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```powershell
cd nexzy-frontend
npm run dev
```

**AI Service:**
```powershell
cd ai-service
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

## Service URLs

- **Frontend**: http://localhost:5174
- **Backend API**: http://127.0.0.1:8000
- **Backend Docs**: http://127.0.0.1:8000/docs
- **AI Service**: http://127.0.0.1:8001
- **AI Docs**: http://127.0.0.1:8001/docs

## Common Tasks

### Running a Scan

1. Open frontend: http://localhost:5174
2. Login with your account
3. Click "NEW SCAN"
4. Enter keywords: `ui.ac.id`
5. Check "Auto Discover"
6. Click "Start Scan"

### Checking Alerts

1. Dashboard shows alert count
2. Click "Alerts" in navigation
3. Filter by severity/status
4. Click alert to view details

### Running Tests

**Backend:**
```powershell
cd nexzy-backend
pytest tests/
```

**Frontend:**
```powershell
cd nexzy-frontend
npm test
```

## Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
AI_SERVICE_URL=http://localhost:8001
```

### Frontend (.env)
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### AI Service (.env)
```env
GEMINI_API_KEY=your_gemini_api_key
```

## Troubleshooting

### Port Already in Use

**Check what's using a port:**
```powershell
netstat -ano | findstr :8000
```

**Kill process by PID:**
```powershell
taskkill /PID <pid> /F
```

### Backend Won't Start

1. Check .env file exists
2. Verify Supabase credentials
3. Check Python version: `python --version`
4. Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Won't Start

1. Check Node version: `node --version`
2. Clear cache: `npm cache clean --force`
3. Reinstall: `rm -rf node_modules; npm install`
4. Check port 5174 is free

### AI Service Issues

1. Check GEMINI_API_KEY in .env
2. Verify API key at: https://aistudio.google.com/app/apikey
3. Check internet connection
4. Backend works without AI (graceful degradation)

## Database Commands

### Run Migrations

```sql
-- In Supabase SQL Editor:
-- Copy from: nexzy-backend/supabase_schema.sql
```

### Check Tables

```sql
SELECT * FROM scans LIMIT 10;
SELECT * FROM alerts ORDER BY created_at DESC LIMIT 10;
SELECT * FROM user_profiles;
```

## Git Commands

### Initial Commit

```bash
git init
git add .
git commit -m "initial commit: nexzy osint platform"
git branch -M main
git remote add origin https://github.com/yourusername/nexzy.git
git push -u origin main
```

### Regular Workflow

```bash
git add .
git commit -m "feat: add new feature"
git push
```

## Useful Endpoints

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Get Stats
```bash
curl http://127.0.0.1:8000/api/stats -H "Authorization: Bearer YOUR_TOKEN"
```

### Test AI Service
```bash
curl http://127.0.0.1:8001/health
```

## Documentation

- [Main README](../README.md)
- [Setup Guides](setup/)
- [Feature Docs](features/)
- [User Guides](guides/)
- [API Docs](http://127.0.0.1:8000/docs) (when running)

## Support

- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- Email: support@nexzy.dev

---

**Keep this file handy for quick reference! 📌**
