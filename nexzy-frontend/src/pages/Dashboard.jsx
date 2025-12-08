import React, { useState, useEffect } from 'react';
import { AlertCircle, ShieldCheck, Key, Activity, Plus } from 'lucide-react';
import StatsCard from '../components/dashboard/StatsCard';
import TrendGraph from '../components/dashboard/TrendGraph';
import RecentAlerts from '../components/dashboard/RecentAlerts';
import ScanModal from '../components/ScanModal';
import ScanNotification from '../components/ScanNotification';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    newAlerts: 0,
    totalCredentials: 0,
    criticalThreats: 0,
    resolved: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);
  const [activeScan, setActiveScan] = useState(null);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    console.log('[DASHBOARD] useEffect triggered, user:', user?.email || 'null');
    
    const loadDashboardData = async () => {
      console.log('[DASHBOARD] loadDashboardData started');
      try {
        // Prefer aggregated backend stats
        let s;
        try {
          console.log('[DASHBOARD] Attempting api.getStats()...');
          s = await api.getStats();
          console.log('[DASHBOARD] api.getStats() succeeded');
        } catch (authErr) {
          console.warn('[DASHBOARD] api.getStats() failed, using fallback:', authErr.message);
          // Fallback to unauthenticated fetch if JWT not available
          const baseUrl = import.meta.env.VITE_API_URL;
          console.log('[DASHBOARD] Fallback fetch to:', `${baseUrl}/api/stats`);
          const res = await fetch(`${baseUrl}/api/stats`, { credentials: 'include' });
          console.log('[DASHBOARD] Fallback response status:', res.status);
          if (!res.ok) throw new Error(`Fallback stats fetch failed: ${res.status}`);
          s = await res.json();
          console.log('[DASHBOARD] Fallback succeeded');
        }
        console.log('[DASHBOARD] /api/stats:', s);
        const newAlerts = s.new_alerts ?? 0;
        const totalCredentials = s.credentials_leaked ?? 0;
        const criticalThreats = s.alerts_critical ?? 0;
        const resolved = s.alerts_resolved ?? 0;

        console.log('[DASHBOARD] Mapped stats:', { newAlerts, totalCredentials, criticalThreats, resolved });
        setStats({ newAlerts, totalCredentials, criticalThreats, resolved });
        setLoading(false);
        console.log('[DASHBOARD] Stats updated successfully');
      } catch (err) {
        console.error('[DASHBOARD] Failed to load dashboard data:', err);
        // Leave existing state values; show error banner
        setError(err.message);
        setLoading(false);
      }
    };
    
    loadDashboardData();
  }, [user]);

  // WebSocket for real-time scan updates
  useEffect(() => {
    if (!user) return;

    const websocket = api.connectWebSocket((message) => {
      console.log('[WS] Received:', message);
      
      if (message.type === 'scan_update') {
        setActiveScan(message.data);
        
        // If scan completed, refresh data after 2 seconds
        if (message.data.status === 'completed') {
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        }
      }
    });

    setWs(websocket);

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [user]);

  const handleScanCreated = (result) => {
    console.log('New scan created:', result);
    setActiveScan({
      scan_id: result.scan_id,
      status: 'pending',
      progress: 0
    });
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Scan Notification */}
      <ScanNotification 
        scan={activeScan} 
        onClose={() => setActiveScan(null)}
      />
      {/* 1. Header with Typing Effect (Optional CSS animation) */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            System <span className="text-red">Overview</span>
          </h1>
          <p className="text-grey font-mono text-sm">
            {loading ? 'Loading...' : error ? 'Error loading data' : `Monitoring active threat vectors... (${user?.email})`}
          </p>
        </div>
        <button 
          onClick={() => setIsScanModalOpen(true)}
          className="bg-skyblue text-black px-6 py-3 rounded-lg font-bold hover:bg-white transition-colors flex items-center gap-2 group"
        >
          <Plus size={20} className="group-hover:rotate-90 transition-transform" />
          NEW SCAN
        </button>
      </div>

      {/* Scan Modal */}
      <ScanModal 
        isOpen={isScanModalOpen} 
        onClose={() => setIsScanModalOpen(false)}
        onScanCreated={handleScanCreated}
      />

      {/* 2. Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard 
          title="New Alerts" 
          value={stats.newAlerts} 
          icon={AlertCircle} 
          color="text-red" 
          trend="+2 this week"
        />
        <StatsCard 
          title="Credentials Leaked" 
          value={stats.totalCredentials} 
          icon={Key} 
          color="text-orange" 
          trend="+15% avg"
        />
        <StatsCard 
          title="Critical Threats" 
          value={stats.criticalThreats} 
          icon={Activity} 
          color="text-yellow" 
          trend="Stable"
        />
        <StatsCard 
          title="Resolved" 
          value={stats.resolved} 
          icon={ShieldCheck} 
          color="text-green" 
          trend="Today"
        />
      </div>

      {/* 3. Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[400px]">
        <TrendGraph />
        <RecentAlerts />
      </div>
    </div>
  );
};

export default Dashboard;