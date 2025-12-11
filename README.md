# 🛡️ Nexzy - OSINT Credential Leak Detection System

<div align="center">

![Nexzy Banner](./image/banner.png)

**AI-Powered credential leak detection for educational institutions and organizations**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19.2.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

[Features](#-features) • [Demo](#-demo) • [Installation](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**Nexzy** is an advanced OSINT (Open Source Intelligence) platform designed to detect and monitor credential leaks across public paste sites and darkweb sources. Built specifically for educational institutions and organizations to protect their digital assets and student data.

### 🎯 Key Capabilities

- 🔍 **Automated Scanning** - Search clearnet & darkweb paste sites automatically
- 🤖 **AI-Powered Analysis** - Gemini AI scores vulnerabilities and generates mitigation recommendations
- 🚨 **Real-Time Alerts** - WebSocket-based instant notifications
- 🌐 **Multi-Source Discovery** - Pastebin, darkweb mirrors, author crawling
- 📊 **Interactive Dashboard** - Modern UI with real-time stats and analytics
- 🛡️ **Smart Detection** - Pattern matching for NPM, emails, passwords, API keys, PII

---

## ✨ Features

### 🔎 Advanced Discovery Engine

- **Keyword Search** - Search paste sites by domain/keywords (e.g., `ui.ac.id`)
- **Pastebin Search Integration** - Direct search using Pastebin's search functionality
- **Darkweb Monitoring** - Scan darkweb paste sites via clearnet mirrors
- **Author Crawling** - Follow paste authors to discover related leaks
- **Direct URL Scanning** - Analyze specific paste URLs

### 🤖 AI-Powered Intelligence

- **Vulnerability Scoring** (0-100) - Automated risk assessment using Gemini AI
- **Smart Summarization** - One-sentence leak descriptions
- **Signal Detection** - Identifies passwords, API keys, database credentials, PII, etc.
- **Mitigation Recommendations** - Actionable steps (Immediate, Short-term, Long-term)
- **Risk Rationale** - Detailed explanations of threats

### 📊 Real-Time Monitoring

- **WebSocket Notifications** - Live scan progress updates
- **Scan Logs Viewer** - Detailed execution logs with timestamps
- **Multi-University Support** - Configure target domains and keywords per user
- **Quick Scan** - One-click scanning with saved settings

### 🎨 Modern User Experience

- **Interactive Dashboard** - Stats, alerts, recent activity
- **Alert Management** - View, investigate, and resolve alerts
- **Advanced Search** - Filter alerts by severity, status, date
- **Dark Theme** - Beautiful glass-morphism design
- **Responsive UI** - Works on desktop and mobile

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Backend & AI Service)
- **Node.js 18+** (Frontend)
- **Supabase Account** (Database & Auth)
- **Gemini API Key** (AI Features - FREE tier available)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/nexzy.git
cd nexzy
```

### 2. Backend Setup

```bash
cd nexzy-backend
pip install -r requirements.txt
```

Create `.env`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
AI_SERVICE_URL=http://localhost:8001
```

Run database migrations:
```sql
-- Run SQL from nexzy-backend/supabase_schema.sql in Supabase SQL Editor
```

Start backend:
```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup

```bash
cd nexzy-frontend
npm install
```

Create `.env`:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

Start frontend:
```bash
npm run dev
```

### 4. AI Service Setup (Optional but Recommended)

```bash
cd ai-service
pip install -r requirements.txt
```

Create `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
```

Get free API key: [Google AI Studio](https://aistudio.google.com/app/apikey)

Start AI service:
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

### 5. Access Application

- **Frontend**: http://localhost:5174
- **Backend API**: http://127.0.0.1:8000
- **AI Service**: http://127.0.0.1:8001
- **API Docs**: http://127.0.0.1:8000/docs

---

## 📸 Demo

### Dashboard
![Dashboard](./image/dashboard.png)
*Real-time monitoring dashboard with stats and alerts*

### Alert Details
![Alert Details](./image/alert-details.png)
*Detailed alert view with AI analysis and mitigation recommendations*

### Scan Management
![Scan Modal](./image/scan-modal.png)
*Configure and launch scans with multiple options*

---

## 🏗️ Architecture

```
nexzy/
├── nexzy-frontend/          # React + Vite frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── lib/             # API client, utilities
│   │   └── contexts/        # React contexts (Auth, Toast)
│   └── package.json
│
├── nexzy-backend/           # FastAPI backend
│   ├── api/                 # API endpoints
│   │   └── main.py         # Main FastAPI app
│   ├── lib/                # Core libraries
│   │   ├── auth.py         # JWT authentication
│   │   ├── ai_client.py    # AI service client
│   │   └── supabase_client.py
│   ├── scrapers/           # OSINT scrapers
│   │   └── discovery_engine.py
│   ├── config.py           # Configuration
│   └── requirements.txt
│
├── ai-service/             # AI scoring microservice
│   ├── main.py            # Gemini API integration
│   └── requirements.txt
│
└── docs/                  # Documentation
    ├── setup/            # Setup guides
    ├── features/         # Feature documentation
    └── guides/           # User guides
```

### Tech Stack

**Frontend:**
- React 19.2.0
- Vite 7.2.6
- Tailwind CSS 4.1.17
- React Router DOM 7.9.6
- Anime.js (animations)

**Backend:**
- FastAPI 0.115.12
- Supabase (PostgreSQL + Auth)
- Uvicorn 0.34.0
- BeautifulSoup4 (scraping)
- SlowAPI (rate limiting)

**AI Service:**
- Google Gemini 2.0 Flash
- FastAPI
- Async processing

---

## 📚 Documentation

### Setup Guides
- [Complete Installation Guide](docs/setup/INSTALLATION.md)
- [Database Setup & Migration](docs/setup/DATABASE_SETUP.md)
- [AI Service Configuration](docs/setup/AI_SERVICE_SETUP.md)

### Feature Documentation
- [Pastebin Search Feature](docs/features/PASTEBIN_SEARCH.md)
- [Darkweb Monitoring](docs/features/DARKWEB_MONITORING.md)
- [AI Analysis & Mitigation](docs/features/AI_ANALYSIS.md)
- [WebSocket Notifications](docs/features/WEBSOCKET_NOTIFICATIONS.md)

### User Guides
- [Quick Start Guide](docs/guides/QUICK_START.md)
- [Creating Your First Scan](docs/guides/FIRST_SCAN.md)
- [Proof of Concept Testing](docs/guides/POC_TESTING.md)

### API Documentation
- Interactive API docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 🎯 Use Cases

### Educational Institutions
- Monitor student credential leaks
- Protect university email domains
- Detect database dumps with student data
- Automated breach notifications

### Organizations
- Corporate credential monitoring
- API key leak detection
- Employee data protection
- Compliance requirements

### Security Research
- OSINT investigations
- Breach analysis
- Threat intelligence gathering
- Vulnerability assessment

---

## 🔒 Security & Privacy

- **No Data Collection** - Only scans public sources
- **Encrypted Storage** - All credentials hashed
- **JWT Authentication** - Secure user sessions
- **Rate Limiting** - API abuse prevention
- **RLS Policies** - Row-level security in database
- **CORS Protection** - Restricted origins

---

## 🛠️ Development

### Project Structure
```
nexzy/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
├── docs/                        # Documentation
├── image/                       # Screenshots & assets
├── nexzy-frontend/              # React frontend
├── nexzy-backend/               # FastAPI backend
└── ai-service/                  # AI microservice
```

### Running Tests

**Backend:**
```bash
cd nexzy-backend
pytest tests/
```

**Frontend:**
```bash
cd nexzy-frontend
npm test
```

### Code Style

- **Python**: PEP 8, Black formatter
- **JavaScript**: ESLint, Prettier
- **Commits**: Conventional Commits

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [React](https://reactjs.org/) - UI library
- [Supabase](https://supabase.com/) - Backend as a Service
- [Google Gemini](https://ai.google.dev/) - AI analysis
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Anime.js](https://animejs.com/) - Animations

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/nexzy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/nexzy/discussions)
- **Email**: support@nexzy.dev

---

## 🌟 Star History

If you find Nexzy useful, please consider giving it a star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/nexzy&type=Date)](https://star-history.com/#yourusername/nexzy&Date)

---

<div align="center">

**Built with ❤️ for cybersecurity and education**

[⬆ Back to Top](#-nexzy---osint-credential-leak-detection-system)

</div>
