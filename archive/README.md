# Nexzy Backend 🔍

**Production-ready FastAPI backend for Nexzy: Project NEXT Intelligence**  
An OSINT platform for detecting leaked university credentials across paste sites.

## 🎯 Features

- ✅ **JWT Authentication**: Supabase-powered user authentication
- ✅ **Database Integration**: Direct Supabase PostgreSQL connection
- ✅ **Background Tasks**: Async scan processing without blocking
- ✅ **Real-time Updates**: WebSocket support for live scan progress
- ✅ **Discovery Engine**: Automated paste site scraping with relevance scoring
- ✅ **RESTful API**: Complete CRUD operations for scans and results

## 📁 Project Structure

```
nexzy-backend/
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI application with all endpoints
├── lib/
│   ├── __init__.py
│   ├── supabase_client.py   # Supabase database client
│   └── auth.py              # JWT authentication middleware
├── scrapers/
│   ├── __init__.py
│   └── discovery_engine.py  # Core OSINT discovery logic
├── tests/
│   └── __init__.py          # Test suite (to be implemented)
├── logs/                    # Application logs (auto-created)
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account
- PostgreSQL database (via Supabase)

### 1. Clone & Setup

```powershell
cd nexzy-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```powershell
cp .env.example .env
```

**Required variables:**

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
TARGET_DOMAIN=ui.ac.id
```

**Get Supabase credentials:**

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Open your project → **Settings** → **API**
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **service_role key** → `SUPABASE_SERVICE_ROLE_KEY` (⚠️ Keep secret!)
   - **JWT Secret** → `SUPABASE_JWT_SECRET`

### 3. Run the Backend

```powershell
# Development mode (auto-reload)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Backend will start at: **http://localhost:8000**

### 4. Verify Installation

Open browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Authentication

All endpoints (except `/health`) require JWT authentication:

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API information | ❌ |
| GET | `/health` | Health check | ❌ |
| POST | `/api/scan` | Create new scan | ✅ |
| GET | `/api/scans` | List user's scans | ✅ |
| GET | `/api/results/{scan_id}` | Get scan results | ✅ |
| WS | `/ws` | WebSocket for real-time updates | ❌ |

### Example Usage

#### 1. Create a Scan

```bash
curl -X POST "http://localhost:8000/api/scan" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://pastebin.com/ABC123",
      "https://paste.ee/p/XYZ789"
    ],
    "enable_clearnet": true,
    "enable_darknet": false,
    "crawl_authors": true
  }'
```

**Response:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Scan created and queued for processing",
  "created_at": "2025-11-30T12:34:56.789Z"
}
```

#### 2. List Scans

```bash
curl "http://localhost:8000/api/scans" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Get Results

```bash
curl "http://localhost:8000/api/results/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔌 WebSocket Integration

Connect to receive real-time scan updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'scan_started':
      console.log('Scan started:', message.scan_id);
      break;
    case 'scan_progress':
      console.log('Progress:', message.progress);
      break;
    case 'scan_completed':
      console.log('Completed! Results:', message.total_results);
      break;
    case 'scan_failed':
      console.error('Failed:', message.error);
      break;
  }
};

// Heartbeat
setInterval(() => ws.send('ping'), 30000);
```

## 🗄️ Database Schema

This backend expects the following Supabase tables (see frontend's schema):

### `scans` table
```sql
- id (uuid, primary key)
- user_id (uuid, foreign key to auth.users)
- status (text: 'queued', 'running', 'completed', 'failed')
- progress (float: 0.0-1.0)
- total_results (integer)
- urls (jsonb)
- options (jsonb)
- error (text, nullable)
- created_at (timestamp)
- updated_at (timestamp)
```

### `scan_results` table
```sql
- id (uuid, primary key)
- scan_id (uuid, foreign key to scans)
- user_id (uuid, foreign key to auth.users)
- url (text)
- source (text)
- author (text)
- relevance_score (float)
- emails (jsonb array)
- target_emails (jsonb array)
- has_credentials (boolean)
- found_at (timestamp)
```

## 🔧 Configuration

All configuration is managed in `config.py` and loaded from environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGET_DOMAIN` | `ui.ac.id` | Domain to monitor |
| `REQUEST_DELAY` | `2.0` | Delay between requests (seconds) |
| `MAX_RETRIES` | `3` | Max retry attempts |
| `MIN_RELEVANCE_SCORE` | `0.3` | Minimum relevance (0.0-1.0) |
| `API_PORT` | `8000` | Server port |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed frontend origins |

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=scrapers --cov=lib

# Run specific test file
pytest tests/test_api.py -v
```

## 🐛 Troubleshooting

### "Import supabase could not be resolved"

```powershell
pip install supabase python-dotenv
```

### "Missing required environment variables"

Ensure your `.env` file has all required variables set (see `.env.example`).

### "Database connection failed"

1. Verify Supabase credentials are correct
2. Check project is not paused on Supabase dashboard
3. Verify service role key (not anon key) is being used

### "CORS error from frontend"

Add your frontend URL to `CORS_ORIGINS` in `.env`:
```env
CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

## 📝 Development

### Adding New Endpoints

1. Add endpoint function to `api/main.py`
2. Use `Depends(get_current_user)` for authenticated routes
3. Update this README with endpoint documentation

### Modifying Discovery Logic

Edit `scrapers/discovery_engine.py`:
- `_calculate_relevance_score()`: Adjust scoring algorithm
- `analyze_paste()`: Change paste analysis logic
- `crawl_user_pastes()`: Modify author crawling behavior

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```powershell
# Build
docker build -t nexzy-backend .

# Run
docker run -p 8000:8000 --env-file .env nexzy-backend
```

### Manual Deployment

1. Set up Python 3.11+ environment
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables in production
4. Run with production ASGI server:
   ```bash
   gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

## 📚 API Documentation

Interactive API docs automatically generated at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Integration with Frontend

This backend is designed to work with the **nexzy-frontend** React application.

**Frontend should:**
1. Obtain JWT token via Supabase authentication
2. Include token in `Authorization: Bearer <token>` header
3. Connect to WebSocket at `/ws` for real-time updates
4. Call `/api/scan` to create scans
5. Poll `/api/scans` or listen to WebSocket for updates
6. Fetch results from `/api/results/{scan_id}` when completed

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built with ❤️ for Nexzy: Project NEXT Intelligence**
