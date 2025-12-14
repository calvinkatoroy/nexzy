# 🐳 Nexzy - Docker Deployment Guide

Complete guide for deploying Nexzy using Docker locally and to cloud platforms.

---

## 📋 Table of Contents

1. [Local Docker Deployment](#-local-docker-deployment)
2. [Cloud Deployment Options](#-cloud-deployment-options)
3. [Recommended: Railway Deployment](#-recommended-railway-deployment)
4. [Alternative: Render Deployment](#-alternative-render-deployment)
5. [Alternative: DigitalOcean](#-alternative-digitalocean-app-platform)
6. [Production Checklist](#-production-checklist)

---

## 🏠 Local Docker Deployment

### Prerequisites
- Docker Desktop installed ([download](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (included with Docker Desktop)

### Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd nexzy

# 2. Copy environment file
cp .env.docker .env

# 3. Edit .env with your actual credentials
# - Supabase URL, keys
# - Gemini API key
notepad .env

# 4. Build and start all services
docker-compose up -d

# 5. Check status
docker-compose ps

# 6. View logs
docker-compose logs -f
```

### Access Services
- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8001/docs
- **AI Service**: http://localhost:8000/health

### Useful Commands

```bash
# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View logs for specific service
docker-compose logs -f backend

# Restart a service
docker-compose restart ai-service

# Remove all containers and volumes
docker-compose down -v
```

---

## ☁️ Cloud Deployment Options

### Comparison Table

| Platform | Cost | Ease | Best For | Free Tier |
|----------|------|------|----------|-----------|
| **Railway** | 💰💰 | ⭐⭐⭐⭐⭐ | Fast deployment | $5 credit/month |
| **Render** | 💰 | ⭐⭐⭐⭐ | Free hosting | Yes (750hrs/month) |
| **DigitalOcean** | 💰💰💰 | ⭐⭐⭐ | Full control | No (starts $4/month) |
| **Heroku** | 💰💰💰 | ⭐⭐⭐⭐ | Simple PaaS | No (paid only) |
| **AWS ECS** | 💰💰💰💰 | ⭐⭐ | Enterprise | Complex pricing |

**My Recommendation: Railway** 🚂
- Easiest setup (15 minutes)
- Built-in monitoring
- Auto-deploy from GitHub
- Great for demos and production

---

## 🚂 Recommended: Railway Deployment

### Why Railway?
✅ Automatic HTTPS  
✅ Environment variables UI  
✅ One-click GitHub integration  
✅ Built-in monitoring  
✅ Generous free tier ($5/month credit)  

### Step-by-Step Railway Deployment

#### 1. Sign Up & Create Project
```
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Authorize Railway to access your repo
6. Select the Nexzy repository
```

#### 2. Deploy AI Service
```
1. Click "New" > "Docker Image"
2. Configure:
   - Name: nexzy-ai-service
   - Build: ./ai-service/Dockerfile
   - Port: 8000
3. Add environment variable:
   - GEMINI_API_KEY = your-key-here
4. Deploy
5. Copy the generated URL (e.g., https://nexzy-ai-service.up.railway.app)
```

#### 3. Deploy Backend
```
1. Click "New" > "Docker Image"
2. Configure:
   - Name: nexzy-backend
   - Build: ./nexzy-backend/Dockerfile
   - Port: 8001
3. Add environment variables:
   - SUPABASE_URL = your-supabase-url
   - SUPABASE_SERVICE_ROLE_KEY = your-key
   - SUPABASE_JWT_SECRET = your-secret
   - TARGET_DOMAIN = ui.ac.id
   - AI_SERVICE_URL = https://nexzy-ai-service.up.railway.app
   - CORS_ORIGINS = https://nexzy-frontend.up.railway.app
4. Deploy
5. Copy the generated URL
```

#### 4. Deploy Frontend
```
1. Click "New" > "Docker Image"
2. Configure:
   - Name: nexzy-frontend
   - Build: ./nexzy-frontend/Dockerfile
   - Port: 80
3. Add environment variables:
   - VITE_SUPABASE_URL = your-supabase-url
   - VITE_SUPABASE_ANON_KEY = your-anon-key
   - VITE_API_URL = https://nexzy-backend.up.railway.app
4. Deploy
5. Your app is live! 🎉
```

#### 5. Custom Domain (Optional)
```
1. Go to Frontend service > Settings > Domains
2. Click "Generate Domain" or add custom domain
3. Update CORS_ORIGINS in backend to include new domain
```

### Railway Pricing
- **Free Tier**: $5 credit/month (~100 hours of deployment)
- **Hobby**: $5/month (unlimited)
- **Pro**: $20/month (priority support, metrics)

**Cost Estimate**: ~$8-12/month for all 3 services running 24/7

---

## 🎨 Alternative: Render Deployment

### Why Render?
✅ **Truly free tier** (750 hrs/month per service)  
✅ Auto-deploy from GitHub  
✅ Simple pricing  
❌ Services spin down after inactivity (50s cold start)  

### Quick Setup

#### 1. Create Render Account
```
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" > "Web Service"
```

#### 2. Deploy Each Service
```bash
# For each service (AI, Backend, Frontend):

1. Connect GitHub repo
2. Set build settings:
   - Build Command: docker build -f ./[service]/Dockerfile .
   - Start Command: (auto-detected from Dockerfile)
3. Add environment variables
4. Click "Create Web Service"
```

#### 3. Link Services
```
Update environment variables with generated URLs:
- AI_SERVICE_URL → Render AI service URL
- VITE_API_URL → Render backend URL
- CORS_ORIGINS → Render frontend URL
```

### Render Pricing
- **Free**: $0 (750hrs/month, cold starts)
- **Starter**: $7/service/month (no cold starts)
- **Standard**: $25/service/month (more resources)

**Cost Estimate**: 
- Free: $0 (with cold starts)
- Always-on: $21/month (3 services × $7)

---

## 🌊 Alternative: DigitalOcean App Platform

### Why DigitalOcean?
✅ Full VPS control  
✅ Predictable pricing  
✅ 1-click Docker deployment  
❌ More expensive  
❌ Requires more setup  

### Quick Setup

```bash
# 1. Install doctl CLI
# Download from: https://docs.digitalocean.com/reference/doctl/

# 2. Authenticate
doctl auth init

# 3. Create App
doctl apps create --spec app-spec.yaml

# 4. Monitor deployment
doctl apps list
```

### DigitalOcean Pricing
- **Basic**: $5/service/month (512MB RAM)
- **Professional**: $12/service/month (1GB RAM)

**Cost Estimate**: $15-36/month

---

## ✅ Production Checklist

### Before Deploying

- [ ] All tests passing locally
- [ ] Docker builds successfully (`docker-compose up`)
- [ ] Environment variables documented
- [ ] Database migrations applied to production Supabase
- [ ] Supabase RLS policies enabled
- [ ] CORS origins configured correctly
- [ ] API rate limiting configured
- [ ] Logging configured (Sentry, Datadog, etc.)

### After Deploying

- [ ] Health checks responding (all 3 services)
- [ ] Can login to frontend
- [ ] Can create and run scans
- [ ] WebSocket connections working
- [ ] AI scoring functional
- [ ] Database queries working
- [ ] Logs showing no errors

### Security Checklist

- [ ] HTTPS enabled (automatic on Railway/Render)
- [ ] Environment variables not in code
- [ ] Service role keys only in backend
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (parameterized queries)

---

## 📊 Cost Comparison Summary

| Deployment | Monthly Cost | Uptime | Setup Time | Recommended For |
|------------|--------------|--------|------------|-----------------|
| **Local Docker** | $0 | Manual | 10 min | Development |
| **Railway** | $8-12 | 99.9% | 15 min | **Production/Demo** ✅ |
| **Render Free** | $0 | ~95% (cold starts) | 20 min | Testing |
| **Render Paid** | $21 | 99.9% | 20 min | Production |
| **DigitalOcean** | $15-36 | 99.9% | 30 min | Enterprise |

---

## 🆘 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs [service-name]

# Common issues:
# 1. Environment variables missing → Check .env file
# 2. Port already in use → Change port in docker-compose.yml
# 3. Build failed → Check Dockerfile syntax
```

### Services can't communicate
```bash
# Make sure all services are on same network
docker network ls
docker network inspect nexzy_nexzy-network

# Update AI_SERVICE_URL to use container name:
AI_SERVICE_URL=http://ai-service:8000
```

### Frontend can't reach backend
```bash
# Check CORS settings in backend:
CORS_ORIGINS=http://localhost,http://localhost:80

# Check VITE_API_URL in frontend:
VITE_API_URL=http://localhost:8001
```

---

## 🎓 Next Steps

1. ✅ Test locally with Docker Compose
2. ✅ Choose cloud platform (Railway recommended)
3. ✅ Deploy all 3 services
4. ✅ Test production deployment
5. ✅ Set up monitoring (Railway has built-in)
6. ✅ Configure custom domain (optional)
7. ✅ Set up CI/CD (GitHub Actions)

---

## 📞 Support

- Docker Issues: [Docker Documentation](https://docs.docker.com/)
- Railway: [Railway Docs](https://docs.railway.app/)
- Render: [Render Docs](https://render.com/docs)
- DigitalOcean: [DO Docs](https://docs.digitalocean.com/)

**Happy Deploying! 🚀**
