import React, { useEffect, useRef, useState } from 'react';
import { ArrowLeft, Globe, ShieldAlert, Calendar, Terminal, Loader } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { animate } from 'animejs';
import EvidenceEditor from '../components/EvidenceEditor';
import CredentialTable from '../components/CredentialTable';
import { api } from '../lib/api';

const AlertDetails = () => {
  const { id } = useParams();
  const scoreRef = useRef(null);
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadAlert = async () => {
      try {
        const alertsData = await api.getAlerts();
        const foundAlert = alertsData.find(a => a.id === id);
        
        if (!foundAlert) {
          setError('Alert not found');
          setLoading(false);
          return;
        }
        
        setAlert(foundAlert);
        setLoading(false);
      } catch (err) {
        console.error('Failed to load alert:', err);
        setError(err.message);
        setLoading(false);
      }
    };
    
    loadAlert();
  }, [id]);

  useEffect(() => {
    if (!alert) return;
    
    // Calculate severity score (critical=95, high=75, medium=50, low=25)
    const severityScore = {
      critical: 95,
      high: 75,
      medium: 50,
      low: 25
    }[alert.severity] || 50;
    
    // 1. Severity Score Count-up Animation
    let scoreObj = { val: 0 };
    animate(scoreObj, {
      val: severityScore,
      round: 1,
      duration: 2000,
      ease: 'outExpo',
      update: () => {
        if (scoreRef.current) scoreRef.current.innerText = scoreObj.val;
      }
    });

    // 2. Critical Alert Pulse
    const pulseColor = alert.severity === 'critical' ? 'rgba(255, 75, 75, 0.8)' : 
                       alert.severity === 'high' ? 'rgba(255, 153, 51, 0.8)' :
                       'rgba(255, 204, 0, 0.8)';
    
    animate('.severity-ring', {
      borderColor: ['rgba(255, 255, 255, 0.2)', pulseColor],
      loop: true,
      direction: 'alternate',
      duration: 1500,
      ease: 'inOutSine'
    });
  }, [alert]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto flex items-center justify-center h-96">
        <Loader className="animate-spin text-skyblue" size={48} />
      </div>
    );
  }

  if (error || !alert) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="glass-panel p-8 rounded-2xl text-center">
          <h2 className="text-2xl font-bold text-red mb-4">Alert Not Found</h2>
          <p className="text-grey mb-6">{error || 'The alert you are looking for does not exist.'}</p>
          <Link to="/alerts" className="text-skyblue hover:text-white transition-colors">
            ← Back to Alerts
          </Link>
        </div>
      </div>
    );
  }

  const sourceUrl = alert.description.match(/Source: (.+)/)?.[1] || 'Unknown';
  const sourceDomain = sourceUrl.split('/')[2] || 'Pastebin';
  const severityLabel = alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1);
  const severityColor = alert.severity === 'critical' ? 'red' : 
                        alert.severity === 'high' ? 'orange' : 
                        alert.severity === 'medium' ? 'yellow' : 'grey';
  const formattedDate = new Date(alert.created_at).toLocaleString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });

  return (
    <div className="max-w-5xl mx-auto animate-fade-in space-y-8">
      
      {/* Navigation Header */}
      <div className="flex items-center gap-4 text-grey mb-8">
        <Link to="/alerts" className="hover:text-white transition-colors flex items-center gap-2">
          <ArrowLeft size={16} /> Back to Alerts
        </Link>
        <span className="text-white/20">/</span>
        <span className={`text-${severityColor}`}>{severityLabel} Alert</span>
        <span className="text-white/20">/</span>
        <span className="text-white">{alert.id.substring(0, 8)}</span>
      </div>

      {/* Header Card */}
      <div className="glass-panel p-8 rounded-2xl relative overflow-hidden">
        <div className={`absolute top-0 left-0 w-1 h-full ${severityColor === 'red' ? 'bg-red' : severityColor === 'orange' ? 'bg-orange' : severityColor === 'yellow' ? 'bg-yellow' : 'bg-grey'}`} />
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          
          <div className="space-y-4 max-w-2xl">
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded text-xs font-bold uppercase tracking-wider ${
                severityColor === 'red' ? 'bg-red/10 text-red border border-red/20' :
                severityColor === 'orange' ? 'bg-orange/10 text-orange border border-orange/20' :
                severityColor === 'yellow' ? 'bg-yellow/10 text-yellow border border-yellow/20' :
                'bg-grey/10 text-grey border border-grey/20'
              }`}>
                {severityLabel}
              </span>
              <span className="flex items-center gap-2 text-grey text-xs">
                <Calendar size={12} /> {formattedDate}
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white leading-tight">
              {alert.title}
            </h1>
            <div className="flex items-center gap-6 text-sm text-grey">
              <div className="flex items-center gap-2">
                <Globe size={16} className="text-skyblue" />
                <span>Source: <span className="text-white">{sourceDomain}</span></span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldAlert size={16} className="text-orange" />
                <span>Detection: <span className="text-white">PII Pattern Match</span></span>
              </div>
            </div>
          </div>

          {/* Severity Score Circle */}
          <div className="relative group">
            <div className={`severity-ring w-24 h-24 rounded-full border-4 flex items-center justify-center bg-background relative z-10 ${
              severityColor === 'red' ? 'border-red/30' :
              severityColor === 'orange' ? 'border-orange/30' :
              severityColor === 'yellow' ? 'border-yellow/30' :
              'border-grey/30'
            }`}>
              <div className="text-center">
                <span ref={scoreRef} className={`text-3xl font-bold block leading-none ${
                  severityColor === 'red' ? 'text-red' :
                  severityColor === 'orange' ? 'text-orange' :
                  severityColor === 'yellow' ? 'text-yellow' :
                  'text-grey'
                }`}>0</span>
                <span className="text-[10px] text-grey uppercase tracking-widest">Severity</span>
              </div>
            </div>
            {/* Glow Effect behind circle */}
            <div className={`absolute inset-0 blur-xl rounded-full z-0 animate-pulse ${
              severityColor === 'red' ? 'bg-red/20' :
              severityColor === 'orange' ? 'bg-orange/20' :
              severityColor === 'yellow' ? 'bg-yellow/20' :
              'bg-grey/20'
            }`}></div>
          </div>
        </div>
      </div>

      {/* RAW EVIDENCE SECTION */}
      <div>
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Terminal size={20} className="text-lavender" /> 
          Alert Information
        </h3>
        <div className="glass-panel p-6 rounded-xl space-y-4">
          <div>
            <h4 className="text-sm font-bold text-white mb-2">Description</h4>
            <p className="text-grey leading-relaxed">{alert.description}</p>
          </div>
          
          {sourceUrl !== 'Unknown' && (
            <div className="pt-4 border-t border-white/10">
              <h4 className="text-sm font-bold text-white mb-2">Source</h4>
              <a 
                href={sourceUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-skyblue hover:text-white transition-colors flex items-center gap-2 inline-flex"
              >
                <Globe size={16} />
                {sourceUrl}
              </a>
            </div>
          )}
          
          <div className="pt-4 border-t border-white/10">
            <h4 className="text-sm font-bold text-white mb-2">Detection Method</h4>
            <p className="text-grey">Indonesian PII Pattern Detection - Automated scan detected NPM (Nomor Pokok Mahasiswa), Indonesian phone numbers, email addresses, and residential addresses in publicly accessible paste.</p>
          </div>
        </div>
      </div>

      {/* SAMPLE CREDENTIALS */}
      <div>
        <h3 className="text-lg font-bold text-white mb-4">Detected Data Types</h3>
        <CredentialTable credentials={[
          { id: 'PII-001', type: 'NPM', email: '1906XXXXXX (Student ID)', domain: 'ui.ac.id', exposure: 'Plaintext' },
          { id: 'PII-002', type: 'Email', email: alert.title.includes('UI') ? 'student@ui.ac.id' : 'student@example.com', domain: alert.title.includes('UI') ? 'ui.ac.id' : 'example.com', exposure: 'Plaintext' },
          { id: 'PII-003', type: 'Phone', email: '+62 8XX-XXXX-XXXX (Indonesian)', domain: 'Personal Contact', exposure: 'Plaintext' },
          { id: 'PII-004', type: 'Address', email: 'Residential Address (Jakarta)', domain: 'Personal Info', exposure: 'Plaintext' },
        ]} />
      </div>

    </div>
  );
};

export default AlertDetails;