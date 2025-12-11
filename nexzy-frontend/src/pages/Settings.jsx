import React, { useEffect, useState } from 'react';
import { animate, stagger } from 'animejs';
import { Save, RefreshCw, Settings as SettingsIcon, Globe, Tag } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../lib/api';
import { useToast } from '../contexts/ToastContext';

const Settings = () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    target_domain: 'ui.ac.id',
    target_keywords: ['ui.ac.id', 'universitas indonesia']
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await api.getSettings();
      setSettings({
        target_domain: data.target_domain || 'ui.ac.id',
        target_keywords: data.target_keywords || ['ui.ac.id', 'universitas indonesia']
      });
    } catch (error) {
      console.error('Failed to load settings:', error);
      showToast && showToast('Failed to load settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await api.updateSettings(settings);
      showToast && showToast('Settings saved successfully', 'success');
    } catch (error) {
      console.error('Failed to save settings:', error);
      showToast && showToast('Failed to save settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleKeywordChange = (index, value) => {
    const newKeywords = [...settings.target_keywords];
    newKeywords[index] = value;
    setSettings({ ...settings, target_keywords: newKeywords });
  };

  const addKeyword = () => {
    setSettings({
      ...settings,
      target_keywords: [...settings.target_keywords, '']
    });
  };

  const removeKeyword = (index) => {
    const newKeywords = settings.target_keywords.filter((_, i) => i !== index);
    setSettings({ ...settings, target_keywords: newKeywords });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin text-skyblue" size={32} />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            <SettingsIcon className="inline mr-2 mb-1" size={32} />
            System <span className="text-skyblue">Settings</span>
          </h1>
          <p className="text-grey font-mono text-sm">
            Configure scan targets and monitoring parameters ({user?.email})
          </p>
        </div>
        <button 
          onClick={handleSave}
          disabled={saving}
          className="bg-skyblue text-black px-6 py-3 rounded-lg font-bold hover:bg-white transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? (
            <RefreshCw size={20} className="animate-spin" />
          ) : (
            <Save size={20} />
          )}
          {saving ? 'SAVING...' : 'SAVE CHANGES'}
        </button>
      </div>

      {/* Settings Form */}
      <div className="glass-panel p-8 rounded-xl border border-white/10 space-y-8">
        
        {/* Target Domain */}
        <div>
          <label className="block text-white font-bold mb-2 flex items-center gap-2">
            <Globe size={20} className="text-skyblue" />
            Target Domain
          </label>
          <p className="text-grey text-sm mb-4 font-mono">
            Primary domain to monitor for credentials (e.g., ui.ac.id, itb.ac.id)
          </p>
          <input
            type="text"
            value={settings.target_domain}
            onChange={(e) => setSettings({ ...settings, target_domain: e.target.value })}
            className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-skyblue focus:outline-none transition-colors font-mono"
            placeholder="ui.ac.id"
          />
        </div>

        {/* Target Keywords */}
        <div>
          <label className="block text-white font-bold mb-2 flex items-center gap-2">
            <Tag size={20} className="text-orange" />
            Target Keywords
          </label>
          <p className="text-grey text-sm mb-4 font-mono">
            Keywords to search for in breach sources (min. 2 keywords recommended)
          </p>
          
          <div className="space-y-3">
            {settings.target_keywords.map((keyword, index) => (
              <div key={index} className="flex gap-3">
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => handleKeywordChange(index, e.target.value)}
                  className="flex-1 bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-orange focus:outline-none transition-colors font-mono"
                  placeholder={`Keyword ${index + 1}`}
                />
                {settings.target_keywords.length > 1 && (
                  <button
                    onClick={() => removeKeyword(index)}
                    className="bg-red/20 text-red px-4 rounded-lg hover:bg-red/30 transition-colors font-bold"
                  >
                    REMOVE
                  </button>
                )}
              </div>
            ))}
            
            <button
              onClick={addKeyword}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-grey hover:text-white hover:border-white/30 transition-colors font-mono"
            >
              + ADD KEYWORD
            </button>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-skyblue/10 border border-skyblue/30 rounded-lg p-4">
          <p className="text-skyblue text-sm font-mono">
            <strong>💡 TIP:</strong> Settings apply to Quick Scan feature. Use specific keywords 
            for better accuracy (e.g., "ui.ac.id" instead of just "ui").
          </p>
        </div>

      </div>

      {/* Multi-University Examples */}
      <div className="glass-panel p-6 rounded-xl border border-white/10">
        <h3 className="text-white font-bold mb-4">Multi-University Presets</h3>
        <div className="grid md:grid-cols-3 gap-4">
          <button 
            onClick={() => setSettings({
              target_domain: 'ui.ac.id',
              target_keywords: ['ui.ac.id', 'universitas indonesia']
            })}
            className="bg-white/5 border border-white/10 rounded-lg p-4 text-left hover:border-skyblue/30 transition-colors"
          >
            <div className="text-white font-bold mb-1">Universitas Indonesia</div>
            <div className="text-grey text-sm font-mono">ui.ac.id</div>
          </button>
          <button 
            onClick={() => setSettings({
              target_domain: 'itb.ac.id',
              target_keywords: ['itb.ac.id', 'institut teknologi bandung']
            })}
            className="bg-white/5 border border-white/10 rounded-lg p-4 text-left hover:border-skyblue/30 transition-colors"
          >
            <div className="text-white font-bold mb-1">ITB</div>
            <div className="text-grey text-sm font-mono">itb.ac.id</div>
          </button>
          <button 
            onClick={() => setSettings({
              target_domain: 'ugm.ac.id',
              target_keywords: ['ugm.ac.id', 'universitas gadjah mada']
            })}
            className="bg-white/5 border border-white/10 rounded-lg p-4 text-left hover:border-skyblue/30 transition-colors"
          >
            <div className="text-white font-bold mb-1">UGM</div>
            <div className="text-grey text-sm font-mono">ugm.ac.id</div>
          </button>
        </div>
      </div>

    </div>
  );
};

export default Settings;