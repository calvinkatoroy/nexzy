import React, { useEffect, useState } from 'react';
import { animate, stagger } from 'animejs';
import { Save, User, Shield, Bell, Database, Monitor, Copy, Check } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const SettingsSection = ({ title, icon: Icon, children }) => (
  <div className="settings-section opacity-0 mb-8">
    <div className="flex items-center gap-2 mb-4 border-b border-white/10 pb-2">
      <Icon className="text-skyblue" size={18} />
      <h3 className="text-sm font-bold text-white uppercase tracking-wider">{title}</h3>
    </div>
    <div className="space-y-4">
      {children}
    </div>
  </div>
);

const Toggle = ({ label, checked, onChange }) => (
  <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/5 hover:border-white/10 transition-colors">
    <span className="text-sm text-grey">{label}</span>
    <div 
      onClick={() => onChange(!checked)}
      className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${
        checked ? 'bg-green' : 'bg-white/10'
      }`}
    >
      <div className={`w-3 h-3 bg-white rounded-full absolute top-1 transition-all ${
        checked ? 'left-6' : 'left-1'
      }`} />
    </div>
  </div>
);

const InputField = ({ label, value, onChange, type = "text", readOnly = false }) => (
  <div>
    <label className="text-xs text-grey ml-1 mb-1 block">{label}</label>
    <input 
      type={type} 
      value={value}
      onChange={(e) => onChange && onChange(e.target.value)}
      readOnly={readOnly}
      className="w-full bg-black/30 border border-white/10 rounded px-3 py-2 text-sm text-white font-mono focus:border-lavender outline-none transition-colors disabled:opacity-50" 
    />
  </div>
);

const Settings = () => {
  const { user } = useAuth();
  const [copied, setCopied] = useState(false);
  const [settings, setSettings] = useState({
    displayName: user?.user_metadata?.full_name || 'Agent',
    email: user?.email || '',
    department: 'Threat Intelligence Unit',
    highContrast: false,
    reducedMotion: false,
    criticalAlerts: true,
    dailyDigest: true,
    systemReports: false,
    maxThreads: 12,
    scanInterval: 30
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    animate('.settings-section', {
      opacity: [0, 1],
      y: [20, 0],
      delay: stagger(100),
      easing: 'outQuad'
    });
  }, []);

  const handleSave = () => {
    // Save settings to localStorage
    localStorage.setItem('nexzy_settings', JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const copyApiKey = () => {
    navigator.clipboard.writeText('sk_live_9384759283745928734');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto pb-20">
      
      {/* Header */}
      <div className="flex justify-between items-end mb-10">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">System <span className="text-grey">Configuration</span></h1>
          <p className="text-grey font-mono text-sm">Manage user preferences and node parameters.</p>
        </div>
        <button 
          onClick={handleSave}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-bold transition-colors ${
            saved ? 'bg-green text-white' : 'bg-white text-background hover:bg-skyblue'
          }`}
        >
          {saved ? <><Check size={16} /> SAVED</> : <><Save size={16} /> SAVE CHANGES</>}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Column */}
        <div>
          <SettingsSection title="Profile Settings" icon={User}>
            <div className="flex items-center gap-4 mb-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-grey to-black border border-white/20 flex items-center justify-center text-2xl">
                👨‍💻
              </div>
              <div>
                <button className="text-xs text-skyblue hover:text-white underline">Change Avatar</button>
              </div>
            </div>
            <InputField 
              label="Display Name" 
              value={settings.displayName}
              onChange={(val) => setSettings({...settings, displayName: val})}
            />
            <InputField 
              label="Email Address" 
              value={settings.email}
              readOnly
            />
            <InputField 
              label="Department" 
              value={settings.department}
              onChange={(val) => setSettings({...settings, department: val})}
            />
          </SettingsSection>

          <SettingsSection title="Interface" icon={Monitor}>
            <Toggle 
              label="High Contrast Mode" 
              checked={settings.highContrast}
              onChange={(val) => setSettings({...settings, highContrast: val})}
            />
            <Toggle 
              label="Reduced Motion" 
              checked={settings.reducedMotion}
              onChange={(val) => setSettings({...settings, reducedMotion: val})}
            />
            <div className="mt-4">
              <label className="text-xs text-grey ml-1 mb-1 block">Theme Accent</label>
              <div className="flex gap-2">
                <div className="w-6 h-6 rounded bg-red cursor-pointer ring-2 ring-white/50" />
                <div className="w-6 h-6 rounded bg-orange cursor-pointer opacity-50 hover:opacity-100" />
                <div className="w-6 h-6 rounded bg-green cursor-pointer opacity-50 hover:opacity-100" />
                <div className="w-6 h-6 rounded bg-skyblue cursor-pointer opacity-50 hover:opacity-100" />
                <div className="w-6 h-6 rounded bg-lavender cursor-pointer opacity-50 hover:opacity-100" />
              </div>
            </div>
          </SettingsSection>
        </div>

        {/* Right Column */}
        <div>
          <SettingsSection title="Security & API" icon={Shield}>
            <InputField label="Current Password" type="password" value="********" />
            <div className="pt-2">
              <label className="text-xs text-grey ml-1 mb-1 block flex justify-between">
                <span>API Key (Read Only)</span>
                <span className="text-orange text-[10px]">EXPIRES IN 3 DAYS</span>
              </label>
              <div className="relative">
                <input 
                  readOnly 
                  value="sk_live_9384759283745928734" 
                  className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-sm text-grey font-mono" 
                />
                <button 
                  onClick={copyApiKey}
                  className={`absolute right-2 top-2 text-[10px] px-2 rounded transition-colors ${
                    copied ? 'bg-green text-white' : 'bg-white/10 hover:bg-white/20 text-white'
                  }`}
                >
                  {copied ? <><Check size={10} className="inline" /> COPIED</> : <><Copy size={10} className="inline" /> COPY</>}
                </button>
              </div>
            </div>
            <div className="mt-4 p-3 bg-red/10 border border-red/20 rounded flex items-start gap-3">
              <Shield className="text-red shrink-0" size={16} />
              <div>
                <h4 className="text-xs font-bold text-red mb-1">DANGER ZONE</h4>
                <p className="text-[10px] text-grey">Revoking access will disconnect all active crawler nodes immediately.</p>
              </div>
            </div>
          </SettingsSection>

          <SettingsSection title="Notifications" icon={Bell}>
            <Toggle 
              label="Critical Alerts (Push)" 
              checked={settings.criticalAlerts}
              onChange={(val) => setSettings({...settings, criticalAlerts: val})}
            />
            <Toggle 
              label="Daily Digest Email" 
              checked={settings.dailyDigest}
              onChange={(val) => setSettings({...settings, dailyDigest: val})}
            />
            <Toggle 
              label="System Health Reports" 
              checked={settings.systemReports}
              onChange={(val) => setSettings({...settings, systemReports: val})}
            />
          </SettingsSection>

          <SettingsSection title="Crawler Configuration" icon={Database}>
            <InputField 
              label="Max Concurrent Threads" 
              value={settings.maxThreads}
              onChange={(val) => setSettings({...settings, maxThreads: parseInt(val) || 12})}
              type="number"
            />
            <div className="mt-2">
              <label className="text-xs text-grey ml-1 mb-1 block">Scan Interval (Minutes)</label>
              <input type="range" className="w-full accent-green h-1 bg-white/20 rounded-lg appearance-none cursor-pointer" />
              <div className="flex justify-between text-[10px] text-grey font-mono mt-1">
                <span>1m</span>
                <span>30m</span>
                <span>60m</span>
              </div>
            </div>
          </SettingsSection>
        </div>

      </div>
    </div>
  );
};

export default Settings;