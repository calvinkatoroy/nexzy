import React, { useState, useEffect } from 'react';
import { animate, stagger } from 'animejs';
import { AlertTriangle, Database, Shield, Globe, Loader } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';

const RecentAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const alertsData = await api.getAlerts();
      
      // Get recent alerts (limit to 4 for dashboard)
      const recentAlerts = alertsData
        .slice(0, 4)
        .map(alert => ({
          id: alert.id,
          title: alert.title,
          source: alert.description.match(/Source: (.+)/)?.[1]?.split('/')[2] || 'Pastebin',
          severity: alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1),
          time: getTimeAgo(alert.created_at),
          icon: alert.severity === 'critical' ? AlertTriangle : alert.severity === 'high' ? AlertTriangle : Database,
          color: alert.severity === 'critical' ? 'text-red' : alert.severity === 'high' ? 'text-orange' : 'text-yellow'
        }));
      
      setAlerts(recentAlerts);
      setLoading(false);
      
      // Animate only if we have alerts
      if (recentAlerts.length > 0) {
        setTimeout(() => {
          animate('.alert-item', {
            opacity: [0, 1],
            x: [20, 0],
            delay: stagger(100, { start: 1000 }),
            ease: 'outQuad'
          });
        }, 100);
      }
    } catch (err) {
      console.error('Failed to load alerts:', err);
      setLoading(false);
    }
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diff = Math.floor((now - then) / 1000); // seconds
    
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-2xl h-full flex items-center justify-center">
        <Loader className="animate-spin text-skyblue" size={24} />
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 rounded-2xl h-full">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-white font-bold">Recent Alerts</h3>
        <Link to="/alerts" className="text-xs text-skyblue hover:text-white transition-colors">
          View All
        </Link>
      </div>

      <div className="space-y-4">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-grey text-sm">
            <Shield size={32} className="mx-auto mb-2 opacity-30" />
            No alerts yet. Run a scan to discover threats.
          </div>
        ) : (
          alerts.map((alert, i) => (
            <Link 
              to={`/alerts/${alert.id}`} 
              key={i} 
              className="alert-item flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-all group opacity-0 cursor-pointer"
            >
              <div className={`p-2 rounded-lg bg-white/5 ${alert.color} group-hover:scale-110 transition-transform`}>
                <alert.icon size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-white text-sm truncate group-hover:text-skyblue transition-colors">{alert.title}</h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border border-white/10 ${alert.color}`}>
                    {alert.severity}
                  </span>
                  <span className="text-xs text-grey truncate">{alert.source}</span>
                </div>
              </div>
              <span className="text-xs font-mono text-grey">{alert.time}</span>
            </Link>
          ))
        )}
      </div>
    </div>
  );
};

export default RecentAlerts;