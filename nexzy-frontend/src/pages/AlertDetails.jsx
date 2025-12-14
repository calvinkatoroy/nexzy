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
        
        console.log('🔍 Alert data:', foundAlert);
        console.log('📊 Vulnerability score:', foundAlert.vulnerability_score);
        
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
    
    // Use actual RoBERTa vulnerability score if available, otherwise fall back to categorical
    const severityScore = alert.vulnerability_score > 0 ? alert.vulnerability_score : {
      critical: 95,
      high: 75,
      medium: 50,
      low: 25
    }[alert.severity] || 50;
    
    console.log('🎯 Setting score to:', severityScore);
    
    // 1. Severity Score Count-up Animation (simplified - anime.js not working)
    if (scoreRef.current) {
      let current = 0;
      const increment = severityScore / 60; // 60 frames for smooth animation
      const timer = setInterval(() => {
        current += increment;
        if (current >= severityScore) {
          current = severityScore;
          clearInterval(timer);
        }
        if (scoreRef.current) {
          scoreRef.current.innerText = Math.round(current);
        }
      }, 16); // ~60fps
      
      return () => clearInterval(timer);
    }

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

  const sourceUrl = alert.source_url || alert.description.match(/Source: (.+)/)?.[1] || alert.description.match(/Source URL: (.+)/)?.[1] || 'Unknown';
  const sourceDomain = sourceUrl.split('/')[2] || 'Pastebin';
  const severityLabel = alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1);
  
  // Extract content snippet if available
  const contentSnippet = alert.content_snippet || null;
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
            <div className="text-grey leading-relaxed whitespace-pre-wrap">
              {alert.description.split('🛡️ MITIGATION RECOMMENDATIONS:')[0]}
            </div>
          </div>
          
          {alert.description.includes('🛡️ MITIGATION RECOMMENDATIONS:') && (
            <div className="pt-4 border-t border-white/10">
              <h4 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <ShieldAlert size={18} className="text-green" />
                Mitigation Recommendations
              </h4>
              <div className="bg-green/5 border border-green/20 rounded-lg p-4">
                <div className="text-grey leading-relaxed whitespace-pre-wrap">
                  {alert.description.split('🛡️ MITIGATION RECOMMENDATIONS:')[1]?.split('Source URL:')[0]?.trim()}
                </div>
              </div>
            </div>
          )}
          
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

      {/* AI ANALYSIS DEPTH */}
      {(alert.vulnerability_score > 0 || alert.ai_signals?.length > 0) && (
        <div>
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <ShieldAlert size={20} className="text-lavender" />
            AI Risk Analysis
          </h3>
          <div className="glass-panel p-6 rounded-xl space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* RoBERTa Vulnerability Score */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="text-xs text-grey mb-2 font-mono uppercase tracking-wider">RoBERTa Score</div>
                <div className={`text-3xl font-bold ${
                  alert.vulnerability_score >= 80 ? 'text-red' :
                  alert.vulnerability_score >= 60 ? 'text-orange' :
                  alert.vulnerability_score >= 40 ? 'text-yellow' :
                  'text-grey'
                }`}>
                  {alert.vulnerability_score > 0 ? Math.round(alert.vulnerability_score) : 0}
                  <span className="text-base text-grey">/100</span>
                </div>
                <div className="mt-2 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${
                      alert.vulnerability_score >= 80 ? 'bg-red' :
                      alert.vulnerability_score >= 60 ? 'bg-orange' :
                      alert.vulnerability_score >= 40 ? 'bg-yellow' :
                      'bg-grey'
                    }`}
                    style={{ width: `${alert.vulnerability_score}%` }}
                  />
                </div>
              </div>

              {/* AI Confidence */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="text-xs text-grey mb-2 font-mono uppercase tracking-wider">Confidence</div>
                <div className="text-3xl font-bold text-skyblue">
                  {alert.ai_confidence ? Math.round(alert.ai_confidence * 100) : 0}
                  <span className="text-base text-grey">%</span>
                </div>
                <div className="text-xs text-grey mt-2">
                  {alert.ai_confidence >= 0.8 ? 'Very High' :
                   alert.ai_confidence >= 0.6 ? 'High' :
                   alert.ai_confidence >= 0.4 ? 'Medium' :
                   'Low'} certainty assessment
                </div>
              </div>

              {/* Signals Detected */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="text-xs text-grey mb-2 font-mono uppercase tracking-wider">Signals Detected</div>
                <div className="text-3xl font-bold text-orange">
                  {alert.ai_signals?.length || 0}
                </div>
                <div className="text-xs text-grey mt-2">Security patterns found</div>
              </div>
            </div>

            {/* Detected Signals Breakdown */}
            {alert.ai_signals && alert.ai_signals.length > 0 && (
              <div className="border-t border-white/10 pt-6">
                <h4 className="text-sm font-bold text-white mb-3">Detected Security Signals</h4>
                <div className="flex flex-wrap gap-2">
                  {alert.ai_signals.map((signal, idx) => (
                    <span 
                      key={idx}
                      className="px-3 py-1 bg-red/10 text-red border border-red/20 rounded-full text-xs font-mono uppercase tracking-wider"
                    >
                      {signal}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Risk Factors */}
            <div className="border-t border-white/10 pt-6">
              <h4 className="text-sm font-bold text-white mb-3">Risk Assessment</h4>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${alert.vulnerability_score >= 80 ? 'bg-red' : 'bg-grey/30'}`} />
                  <div>
                    <div className="text-sm text-white font-medium">Critical Exposure Level</div>
                    <div className="text-xs text-grey">
                      {alert.vulnerability_score >= 80 ? 'Immediate action required - sensitive data publicly accessible' : 'Not detected'}
                    </div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${alert.ai_signals?.some(s => s.toLowerCase().includes('credential')) ? 'bg-orange' : 'bg-grey/30'}`} />
                  <div>
                    <div className="text-sm text-white font-medium">Credential Compromise</div>
                    <div className="text-xs text-grey">
                      {alert.ai_signals?.some(s => s.toLowerCase().includes('credential')) ? 'Credentials or API keys detected in paste' : 'No credentials detected'}
                    </div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${alert.ai_signals?.some(s => s.toLowerCase().includes('email')) ? 'bg-yellow' : 'bg-grey/30'}`} />
                  <div>
                    <div className="text-sm text-white font-medium">PII Exposure</div>
                    <div className="text-xs text-grey">
                      {alert.ai_signals?.some(s => s.toLowerCase().includes('email')) ? 'Personal identifiable information exposed' : 'No PII patterns found'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

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

      {/* PASTE CONTENT SNIPPET */}
      {(contentSnippet || sourceUrl !== 'Unknown') && (
        <div>
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Terminal size={20} className="text-skyblue" />
            Paste Content Preview
          </h3>
          <a
            href={sourceUrl !== 'Unknown' ? sourceUrl : '#'}
            target="_blank"
            rel="noopener noreferrer"
            className={`block glass-panel p-6 rounded-xl border-2 transition-all ${
              sourceUrl !== 'Unknown' 
                ? 'border-skyblue/20 hover:border-skyblue/50 hover:bg-white/10 cursor-pointer group' 
                : 'border-white/10 cursor-default'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="text-xs text-grey font-mono uppercase tracking-wider flex items-center gap-2">
                <Globe size={14} className="text-skyblue" />
                Click to view full paste
              </div>
              {sourceUrl !== 'Unknown' && (
                <div className="text-xs text-skyblue opacity-60 group-hover:opacity-100 transition-opacity">
                  Open in new tab →
                </div>
              )}
            </div>
            <div className="font-mono text-sm text-grey leading-relaxed whitespace-pre-wrap max-h-64 overflow-hidden relative">
              {contentSnippet || 'Content preview not available. Click to view the full paste.'}
              {contentSnippet && (
                <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-background to-transparent" />
              )}
            </div>
            {sourceUrl !== 'Unknown' && (
              <div className="mt-4 pt-4 border-t border-white/10 text-xs text-skyblue group-hover:text-white transition-colors flex items-center gap-2">
                <Globe size={12} />
                <span className="truncate">{sourceUrl}</span>
              </div>
            )}
          </a>
        </div>
      )}

    </div>
  );
};

export default AlertDetails;