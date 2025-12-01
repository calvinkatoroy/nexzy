# Nexzy Frontend ↔️ Backend Integration Guide

This guide shows how to connect your React frontend (`nexzy-frontend`) with the FastAPI backend (`nexzy-backend`).

## 🔗 Architecture Overview

```
┌─────────────────────────┐
│   React Frontend        │
│   (nexzy-frontend)      │
│   Port: 5173            │
└────────┬────────────────┘
         │
         ├─────────────────┐
         │                 │
    ┌────▼──────┐    ┌─────▼──────────┐
    │ Supabase  │    │ FastAPI Backend│
    │   Auth    │    │ (nexzy-backend)│
    │   DB      │    │   Port: 8000   │
    └───────────┘    └────────┬───────┘
                              │
                         ┌────▼─────┐
                         │ Supabase │
                         │    DB    │
                         └──────────┘
```

**Data Flow:**
1. Frontend authenticates user with Supabase → Gets JWT token
2. Frontend calls backend API with JWT in header
3. Backend verifies JWT, processes request
4. Backend reads/writes to Supabase database
5. Backend returns data to frontend

---

## 🚀 Quick Setup

### 1. Start Backend

```powershell
cd nexzy-backend
.\start.ps1
```

Backend runs at: `http://localhost:8000`

### 2. Configure Frontend

In `nexzy-frontend`, create or edit `.env`:

```env
# Supabase (for authentication)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Backend API
VITE_API_URL=http://localhost:8000
```

### 3. Start Frontend

```powershell
cd nexzy-frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 📡 Frontend API Client

Create or update `nexzy-frontend/src/api/client.js`:

```javascript
// API Client for Nexzy Backend
import { supabase } from '../lib/supabase'; // Your existing Supabase client

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class NexzyAPI {
  /**
   * Get authentication token from Supabase
   */
  async getAuthToken() {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token;
  }

  /**
   * Make authenticated request
   */
  async request(endpoint, options = {}) {
    const token = await this.getAuthToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  /**
   * Create a new scan
   */
  async createScan(urls, options = {}) {
    return this.request('/api/scan', {
      method: 'POST',
      body: JSON.stringify({
        urls,
        enable_clearnet: options.enableClearnet ?? true,
        enable_darknet: options.enableDarknet ?? false,
        crawl_authors: options.crawlAuthors ?? true,
      }),
    });
  }

  /**
   * List all scans for current user
   */
  async listScans() {
    return this.request('/api/scans');
  }

  /**
   * Get results for a specific scan
   */
  async getScanResults(scanId) {
    return this.request(`/api/results/${scanId}`);
  }

  /**
   * Connect to WebSocket for real-time updates
   */
  connectWebSocket(onMessage) {
    const ws = new WebSocket(`ws://localhost:8000/ws`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      
      // Send heartbeat every 30 seconds
      setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      onMessage(message);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  }

  /**
   * Check API health
   */
  async healthCheck() {
    const response = await fetch(`${API_URL}/health`);
    return response.json();
  }
}

export const nexzyAPI = new NexzyAPI();
```

---

## 🎯 Usage Examples

### Example 1: Create Scan from Dashboard

```jsx
// Dashboard.jsx or similar component
import { nexzyAPI } from '../api/client';
import { useState } from 'react';

export function ScanForm() {
  const [urls, setUrls] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const urlList = urls.split('\n').filter(url => url.trim());
      
      const response = await nexzyAPI.createScan(urlList, {
        enableClearnet: true,
        crawlAuthors: true
      });

      console.log('Scan created:', response.scan_id);
      // Show success message, redirect, etc.
      
    } catch (error) {
      console.error('Failed to create scan:', error);
      // Show error message
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={urls}
        onChange={(e) => setUrls(e.target.value)}
        placeholder="Enter URLs (one per line)"
        rows={5}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Start Scan'}
      </button>
    </form>
  );
}
```

### Example 2: Display Scan History

```jsx
// ScansPage.jsx
import { nexzyAPI } from '../api/client';
import { useEffect, useState } from 'react';

export function ScansPage() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadScans();
  }, []);

  const loadScans = async () => {
    try {
      const data = await nexzyAPI.listScans();
      setScans(data);
    } catch (error) {
      console.error('Failed to load scans:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>My Scans</h1>
      {scans.map(scan => (
        <div key={scan.scan_id} className="scan-card">
          <h3>Scan ID: {scan.scan_id}</h3>
          <p>Status: {scan.status}</p>
          <p>Progress: {(scan.progress * 100).toFixed(0)}%</p>
          <p>Results: {scan.total_results}</p>
          <p>Created: {new Date(scan.created_at).toLocaleString()}</p>
        </div>
      ))}
    </div>
  );
}
```

### Example 3: Real-time Updates with WebSocket

```jsx
// ScanMonitor.jsx
import { nexzyAPI } from '../api/client';
import { useEffect, useState } from 'react';

export function ScanMonitor({ scanId }) {
  const [status, setStatus] = useState('queued');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const ws = nexzyAPI.connectWebSocket((message) => {
      console.log('WebSocket message:', message);

      // Only handle messages for our scan
      if (message.scan_id !== scanId) return;

      switch (message.type) {
        case 'scan_started':
          setStatus('running');
          break;
        
        case 'scan_progress':
          setProgress(message.progress);
          break;
        
        case 'scan_completed':
          setStatus('completed');
          setProgress(1.0);
          // Optionally fetch results
          loadResults();
          break;
        
        case 'scan_failed':
          setStatus('failed');
          console.error('Scan failed:', message.error);
          break;
      }
    });

    return () => ws.close();
  }, [scanId]);

  const loadResults = async () => {
    try {
      const data = await nexzyAPI.getScanResults(scanId);
      console.log('Results:', data);
      // Update UI with results
    } catch (error) {
      console.error('Failed to load results:', error);
    }
  };

  return (
    <div className="scan-monitor">
      <h3>Scan: {scanId}</h3>
      <p>Status: {status}</p>
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${progress * 100}%` }}
        />
      </div>
      <p>{(progress * 100).toFixed(0)}%</p>
    </div>
  );
}
```

### Example 4: Display Results

```jsx
// ResultsPage.jsx
import { nexzyAPI } from '../api/client';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

export function ResultsPage() {
  const { scanId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadResults();
  }, [scanId]);

  const loadResults = async () => {
    try {
      const results = await nexzyAPI.getScanResults(scanId);
      setData(results);
    } catch (error) {
      console.error('Failed to load results:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading results...</div>;
  if (!data) return <div>No results found</div>;

  return (
    <div className="results-page">
      <h1>Scan Results</h1>
      <div className="stats">
        <p>Total Results: {data.total_results}</p>
        <p>Status: {data.status}</p>
      </div>

      <div className="results-list">
        {data.results.map(result => (
          <div key={result.id} className="result-card">
            <h3>{result.url}</h3>
            <p>Author: {result.author}</p>
            <p>Relevance: {(result.relevance_score * 100).toFixed(0)}%</p>
            <p>Emails: {result.emails.length}</p>
            <p>Target Emails: {result.target_emails.length}</p>
            {result.has_credentials && (
              <span className="badge">Credentials Detected</span>
            )}
            <div className="emails">
              {result.target_emails.map((email, i) => (
                <span key={i} className="email-tag">{email}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔐 Authentication Flow

```jsx
// AuthContext.jsx or similar
import { supabase } from '../lib/supabase';
import { nexzyAPI } from '../api/client';

// Check if user is authenticated
const checkAuth = async () => {
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session) {
    // Redirect to login
    return false;
  }

  // Test backend connection
  try {
    const health = await nexzyAPI.healthCheck();
    console.log('Backend health:', health);
    return true;
  } catch (error) {
    console.error('Backend not available:', error);
    return false;
  }
};

// Sign in
const signIn = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });

  if (error) throw error;
  return data;
};

// Sign out
const signOut = async () => {
  await supabase.auth.signOut();
};
```

---

## 🧪 Testing Integration

### Test Backend Connection

```javascript
// In your frontend console
import { nexzyAPI } from './api/client';

// 1. Check health
const health = await nexzyAPI.healthCheck();
console.log(health); // Should show: { status: "healthy", ... }

// 2. Test authentication (after logging in)
const scans = await nexzyAPI.listScans();
console.log(scans); // Should show your scans array

// 3. Create test scan
const result = await nexzyAPI.createScan(['https://pastebin.com/test']);
console.log(result); // Should show: { scan_id: "...", status: "queued" }
```

---

## 🐛 Troubleshooting

### CORS Error

**Error:** `Access to fetch blocked by CORS policy`

**Fix:** Add frontend URL to backend `.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Authentication Failed

**Error:** `401 Unauthorized` or `Invalid authentication credentials`

**Check:**
1. User is logged in via Supabase
2. JWT token is being sent in header
3. Backend has correct `SUPABASE_URL` and `SUPABASE_JWT_SECRET`

### Connection Refused

**Error:** `Failed to fetch` or `Connection refused`

**Check:**
1. Backend is running (`http://localhost:8000/health` should work)
2. Frontend `.env` has correct `VITE_API_URL`
3. No firewall blocking port 8000

### WebSocket Not Connecting

**Error:** WebSocket connection fails

**Check:**
1. Using `ws://` not `wss://` for local development
2. Backend WebSocket endpoint is `/ws`
3. No proxy interfering with WebSocket

---

## 📊 Environment Variables Summary

### Frontend (`.env`)
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8000
```

### Backend (`.env`)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
TARGET_DOMAIN=ui.ac.id
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🚀 Production Deployment

### Backend (e.g., Railway, Render, Fly.io)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
TARGET_DOMAIN=ui.ac.id
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
```

### Frontend (e.g., Vercel, Netlify)

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=https://your-backend.railway.app
```

---

## ✅ Integration Checklist

- [ ] Backend running at `http://localhost:8000`
- [ ] Frontend running at `http://localhost:5173`
- [ ] Both have correct `.env` files
- [ ] Database schema applied in Supabase
- [ ] User can login via Supabase Auth
- [ ] `/health` endpoint returns success
- [ ] Can create scan from frontend
- [ ] WebSocket shows real-time updates
- [ ] Results display correctly

---

**You're ready to go! Happy scanning! 🔍**
