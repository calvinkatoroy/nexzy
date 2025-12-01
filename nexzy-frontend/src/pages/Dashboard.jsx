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
    const loadDashboardData = async () => {
      try {
        const alertsData = await api.getAlerts();
        
        // Calculate stats from real alerts
        const newAlerts = alertsData.filter(a => a.status === 'new' || a.status === 'active').length;
        
        const criticalThreats = alertsData.filter(a => a.severity === 'critical').length;
        const resolved = alertsData.filter(a => a.resolved_at !== null).length;
        
        // Extract credential count from descriptions - try multiple patterns
        const totalCredentials = alertsData.reduce((sum, a) => {
          // Try: "Total X records" or "X records" or default to alert count * 20
          const match1 = a.description.match(/Total (\d+) records/);
          const match2 = a.description.match(/(\d+) target emails/);
          const records = match1 ? parseInt(match1[1]) : (match2 ? parseInt(match2[1]) * 5 : 20);
          return sum + records;
        }, 0);

        console.log('[DASHBOARD] Stats calculated:', { newAlerts, totalCredentials, criticalThreats, resolved });
        setStats({ newAlerts, totalCredentials, criticalThreats, resolved });
        setLoading(false);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    if (user) {
      loadDashboardData();
    }
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