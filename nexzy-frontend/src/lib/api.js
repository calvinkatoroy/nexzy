export async function fetchStats(token) {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
  const res = await fetch(`${baseUrl}/api/stats`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to load stats');
  return res.json();
}
/**
 * Backend API Client
 * Handles all communication with the FastAPI backend
 */

import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

/**
 * Get current user's JWT token
 */
async function getAuthToken() {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token;
}

/**
 * Make authenticated API request
 */
async function fetchAPI(endpoint, options = {}) {
  const token = await getAuthToken();
  
  console.log('🔑 Auth token:', token ? `${token.substring(0, 20)}...` : 'NO TOKEN');
  
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  console.log(`📡 Fetching: ${API_URL}${endpoint}`);
  console.log('📦 Options:', { method: options.method, body: options.body?.substring(0, 100) });

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  console.log(`📨 Response status: ${response.status}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    console.error('❌ API Error:', error);
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  const data = await response.json();
  console.log('✅ Response data:', data);
  return data;
}

/**
 * API Methods
 */
export const api = {
  /**
   * Health check
   */
  async health() {
    const response = await fetch(`${API_URL}/health`);
    return response.json();
  },

  /**
   * Create a new scan
   */
  async createScan(urls, options = {}) {
    return fetchAPI('/api/scan', {
      method: 'POST',
      body: JSON.stringify({
        urls: Array.isArray(urls) ? urls : [urls],
        enable_clearnet: options.enable_clearnet ?? true,
        enable_darknet: options.enable_darknet ?? false,
        crawl_authors: options.crawl_authors ?? true,
      }),
    });
  },

  /**
   * Get all scans for current user
   */
  async getScans() {
    return fetchAPI('/api/scans');
  },

  /**
   * Get specific scan by ID
   */
  async getScanById(scanId) {
    return fetchAPI(`/api/scans/${scanId}`);
  },

  /**
   * Get results for a specific scan
   */
  async getScanResults(scanId) {
    return fetchAPI(`/api/results/${scanId}`);
  },

  /**
   * Get all alerts for current user
   */
  async getAlerts() {
    return fetchAPI('/api/alerts');
  },

  /**
   * Get aggregated dashboard stats
   */
  async getStats() {
    return fetchAPI('/api/stats');
  },

  /**
   * Search scan results with filters
   */
  async search(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.q) queryParams.append('q', params.q);
    if (params.source) queryParams.append('source', params.source);
    if (params.min_score !== undefined) queryParams.append('min_score', params.min_score);
    if (params.has_credentials !== undefined) queryParams.append('has_credentials', params.has_credentials);
    if (params.email_domain) queryParams.append('email_domain', params.email_domain);
    
    const queryString = queryParams.toString();
    return fetchAPI(`/api/search${queryString ? '?' + queryString : ''}`);
  },

  /**
   * Get user settings (target domain & keywords)
   */
  async getSettings() {
    return fetchAPI('/api/settings');
  },

  /**
   * Update user settings
   */
  async updateSettings(settings) {
    return fetchAPI('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  },

  /**
   * Quick scan - one-click scan with current settings
   */
  async quickScan() {
    return fetchAPI('/api/scan/quick', {
      method: 'POST',
    });
  },

  /**
   * WebSocket connection for real-time updates
   */
  connectWebSocket(onMessage) {
    const ws = new WebSocket(`${API_URL.replace('http', 'ws')}/ws`);

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      // Send heartbeat every 30 seconds
      const heartbeat = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 30000);

      ws.addEventListener('close', () => {
        clearInterval(heartbeat);
      });
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        onMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  },
};
