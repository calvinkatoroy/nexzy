import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2, Play, Loader } from 'lucide-react';
import { api } from '../lib/api';
import { useToast } from '../contexts/ToastContext';
import { useWebSocket } from '../hooks/useWebSocket';

const ScanModal = ({ isOpen, onClose, onScanCreated }) => {
  const [urls, setUrls] = useState(['']);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [currentScanId, setCurrentScanId] = useState(null);
  const [crawlAuthors, setCrawlAuthors] = useState(true);
  const [enableDarknet, setEnableDarknet] = useState(false);
  const toast = useToast();

  // WebSocket for real-time scan updates
  useWebSocket((message) => {
    if (message.scan_id === currentScanId) {
      switch (message.type) {
        case 'scan_started':
          toast.info('Scan started! Analyzing paste sites...');
          break;
        case 'scan_progress':
          toast.info(`Progress: ${message.progress}% - ${message.total_results} results found`);
          break;
        case 'scan_completed':
          toast.success(`Scan completed! Found ${message.total_results} results`);
          setCurrentScanId(null);
          break;
        case 'scan_failed':
          toast.error(`Scan failed: ${message.error}`);
          setCurrentScanId(null);
          break;
      }
    }
  });

  const addUrlField = () => {
    setUrls([...urls, '']);
  };

  const removeUrlField = (index) => {
    if (urls.length > 1) {
      setUrls(urls.filter((_, i) => i !== index));
    }
  };

  const updateUrl = (index, value) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Filter out empty URLs
    const validUrls = urls.filter(url => url.trim());
    
    if (validUrls.length === 0) {
      setError('Please enter at least one paste URL');
      return;
    }

    console.log('🚀 Creating scan with URLs:', validUrls);
    setIsSubmitting(true);

    try {
      const result = await api.createScan(validUrls, {
        enable_clearnet: true,
        enable_darknet: enableDarknet,
        crawl_authors: crawlAuthors
      });

      console.log('✅ Scan created:', result);
      setCurrentScanId(result.scan_id);
      toast.success('Scan initiated successfully!');

      // Notify parent and close
      if (onScanCreated) {
        onScanCreated(result);
      }
      onClose();
      
      // Reset form
      setUrls(['']);
    } catch (err) {
      console.error('❌ Scan creation failed:', err);
      setError(err.message || 'Failed to create scan');
      toast.error(err.message || 'Failed to create scan');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div 
        className="glass-panel w-full max-w-2xl rounded-2xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200 border border-white/10"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <h2 className="text-2xl font-bold text-white uppercase">New Scan</h2>
            <p className="text-xs text-grey mt-1 font-mono">INITIATE OSINT DISCOVERY</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors text-grey hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          
          {error && (
            <div className="bg-red/10 border border-red/30 rounded-lg p-3 text-red text-sm">
              {error}
            </div>
          )}

          {/* URL Inputs */}
          <div className="space-y-3">
            <label className="text-xs text-grey uppercase tracking-widest font-mono">
              Paste URLs to Analyze
            </label>
            
            {urls.map((url, index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => updateUrl(index, e.target.value)}
                  placeholder="https://pastebin.com/..."
                  className="flex-1 bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-skyblue outline-none font-mono text-sm"
                />
                {urls.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeUrlField(index)}
                    className="p-3 border border-white/10 rounded-lg hover:bg-red/10 hover:border-red/30 text-grey hover:text-red transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>
            ))}

            <button
              type="button"
              onClick={addUrlField}
              className="w-full border border-dashed border-white/20 rounded-lg py-2 text-grey hover:text-skyblue hover:border-skyblue/50 transition-colors flex items-center justify-center gap-2 text-sm font-mono"
            >
              <Plus size={16} />
              ADD ANOTHER URL
            </button>
          </div>

          {/* Options */}
          <div className="space-y-3 p-4 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-grey uppercase tracking-widest font-mono mb-3">
              Scan Options
            </p>
            
            <label className="flex items-center gap-3 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={crawlAuthors}
                onChange={(e) => setCrawlAuthors(e.target.checked)}
                className="w-4 h-4 accent-skyblue"
              />
              <span className="text-white text-sm group-hover:text-skyblue transition-colors">
                Crawl author profiles (discover additional pastes)
              </span>
            </label>
            
            <label className="flex items-center gap-3 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={enableDarknet}
                onChange={(e) => setEnableDarknet(e.target.checked)}
                className="w-4 h-4 accent-orange"
              />
              <div className="flex-1">
                <span className="text-white text-sm group-hover:text-orange transition-colors">
                  Enable Darkweb Search 🌐
                </span>
                <p className="text-xs text-grey mt-1">
                  Search darkweb paste sites (Stronghold, DarkPaste, etc.) - Slower but finds unlisted pastes
                </p>
              </div>
            </label>
            
            <label className="flex items-center gap-3 cursor-pointer group">
              <input 
                type="checkbox" 
                defaultChecked 
                disabled
                className="w-4 h-4 accent-green"
              />
              <span className="text-grey text-sm">
                Extract credentials and emails (Always enabled)
              </span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 py-3 border border-white/10 rounded-lg text-white hover:bg-white/5 transition-colors font-bold disabled:opacity-50"
            >
              CANCEL
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 py-3 bg-skyblue text-black rounded-lg hover:bg-white transition-colors font-bold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader className="animate-spin" size={18} />
                  SCANNING...
                </>
              ) : (
                <>
                  <Play size={18} />
                  START SCAN
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ScanModal;
