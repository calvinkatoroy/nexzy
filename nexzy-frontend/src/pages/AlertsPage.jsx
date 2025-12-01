import React, { useState, useEffect } from 'react';
import { animate, stagger } from 'animejs';
import { AlertTriangle, CheckCircle, Clock, Filter, MoreVertical, Loader } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const alertsData = await api.getAlerts();
      
      // Convert alerts to display format
      const alertList = alertsData.map(alert => ({
        id: alert.id,
        title: alert.title,
        source: alert.description.match(/Source: (.+)/)?.[1]?.split('/')[2] || 'Pastebin',
        time: getTimeAgo(alert.created_at),
        severity: alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1),
        status: alert.status === 'new' ? 'Active' : alert.status.charAt(0).toUpperCase() + alert.status.slice(1),
        description: alert.description
      }));
      
      setAlerts(alertList);
      setLoading(false);
      
      setTimeout(() => {
        animate('.alert-row', {
          opacity: [0, 1],
          translateX: [-10, 0],
          delay: stagger(50),
          easing: 'outQuad'
        });
      }, 100);
    } catch (err) {
      console.error('Failed to load alerts:', err);
      setLoading(false);
    }
  };

  const getSeverity = (scan) => {
    if (scan.status === 'failed') return 'Low';
    if (scan.credentials_found > 10) return 'Critical';
    if (scan.credentials_found > 5) return 'High';
    if (scan.credentials_found > 0) return 'Medium';
    return 'Low';
  };

  const getStatus = (status) => {
    if (status === 'completed') return 'Resolved';
    if (status === 'failed') return 'Failed';
    if (status === 'running') return 'Investigating';
    return 'Active';
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diff = Math.floor((now - then) / 1000);
    
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto flex items-center justify-center h-64">
        <Loader className="animate-spin text-skyblue" size={48} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">Threat <span className="text-orange">Alerts</span></h1>
        <div className="flex gap-2">
          <button className="p-2 border border-white/10 rounded-lg hover:bg-white/5 text-grey hover:text-white transition-colors">
            <Filter size={18} />
          </button>
          <button className="bg-white/10 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-white/20 transition-colors">
            MARK ALL READ
          </button>
        </div>
      </div>

      <div className="glass-panel rounded-xl overflow-hidden border border-white/10">
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-4 p-4 border-b border-white/10 bg-white/5 text-xs text-grey font-mono uppercase tracking-wider">
          <div className="col-span-1">Sev</div>
          <div className="col-span-5">Alert Description</div>
          <div className="col-span-2">Source</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-2 text-right">Time</div>
        </div>

        {/* List */}
        <div className="divide-y divide-white/5">
          {alerts.length === 0 ? (
            <div className="p-12 text-center text-grey">
              No alerts yet. Create a scan to start monitoring.
            </div>
          ) : (
            alerts.map((alert, i) => (
              <Link 
                to={`/alerts/${alert.id}`}
                key={i} 
                className="alert-row opacity-0 grid grid-cols-12 gap-4 p-4 items-center hover:bg-white/5 transition-colors group cursor-pointer"
              >
                
                {/* Severity Icon */}
                <div className="col-span-1">
                  {alert.severity === 'Critical' && <AlertTriangle className="text-red" size={18} />}
                  {alert.severity === 'High' && <AlertTriangle className="text-orange" size={18} />}
                  {alert.severity === 'Medium' && <Clock className="text-yellow" size={18} />}
                  {alert.severity === 'Low' && <CheckCircle className="text-grey" size={18} />}
                </div>

                {/* Title & ID */}
                <div className="col-span-5">
                  <div className="text-white font-bold text-sm group-hover:text-skyblue transition-colors">{alert.title}</div>
                  <div className="text-[10px] text-grey font-mono">ID: {String(alert.id).substring(0, 8)}</div>
                </div>

                {/* Source */}
                <div className="col-span-2 text-sm text-grey">
                  {alert.source}
                </div>

                {/* Status Badge */}
                <div className="col-span-2">
                  <span className={`text-[10px] px-2 py-1 rounded-full border ${
                    alert.status === 'Active' ? 'border-red/30 bg-red/10 text-red' :
                    alert.status === 'Resolved' ? 'border-green/30 bg-green/10 text-green' :
                    alert.status === 'Failed' ? 'border-grey/30 bg-grey/10 text-grey' :
                    'border-yellow/30 bg-yellow/10 text-yellow'
                  }`}>
                    {alert.status}
                  </span>
                </div>

                {/* Time */}
                <div className="col-span-2 text-right text-xs text-grey font-mono flex items-center justify-end gap-2">
                  {alert.time}
                  <MoreVertical size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>

              </Link>
            ))
          )}
        </div>
      </div>

    </div>
  );
};

export default AlertsPage;