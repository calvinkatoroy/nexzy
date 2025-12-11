import React, { useEffect, useState } from 'react';
import { animate } from 'animejs';
import { Loader, CheckCircle, AlertTriangle, X, FileText } from 'lucide-react';

const ScanNotification = ({ scan, onClose, onViewLogs }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (scan) {
      setProgress(scan.progress * 100);
      
      // Animate progress bar
      animate('.scan-progress-bar', {
        width: `${scan.progress * 100}%`,
        duration: 500,
        easing: 'outQuad'
      });
    }
  }, [scan]);

  if (!scan) return null;

  const getStatusIcon = () => {
    if (scan.status === 'completed') return <CheckCircle size={20} className="text-green" />;
    if (scan.status === 'failed') return <AlertTriangle size={20} className="text-red" />;
    return <Loader size={20} className="animate-spin text-skyblue" />;
  };

  const getStatusColor = () => {
    if (scan.status === 'completed') return 'border-green/30 bg-green/10';
    if (scan.status === 'failed') return 'border-red/30 bg-red/10';
    return 'border-skyblue/30 bg-skyblue/10';
  };

  const getStatusText = () => {
    // Use message from WebSocket if available
    if (scan.message) return scan.message;
    
    if (scan.status === 'pending') return 'Initializing scan...';
    if (scan.status === 'running') return `Scanning (${Math.round(progress)}%)`;
    if (scan.status === 'completed') return `Scan complete - ${scan.credentials_found || 0} credentials found`;
    if (scan.status === 'failed') return 'Scan failed';
    return 'Processing...';
  };

  return (
    <div className={`fixed top-6 right-6 z-50 w-96 glass-panel rounded-xl border p-4 shadow-2xl animate-in slide-in-from-top ${getStatusColor()}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-sm font-bold text-white">
              {scan.status === 'completed' ? 'Scan Completed' :
               scan.status === 'failed' ? 'Scan Failed' :
               'Scanning...'}
            </h3>
            <p className="text-xs text-grey font-mono">ID: {scan.scan_id?.substring(0, 8)}</p>
          </div>
        </div>
        {(scan.status === 'completed' || scan.status === 'failed') && (
          <button 
            onClick={onClose}
            className="text-grey hover:text-white transition-colors"
          >
            <X size={16} />
          </button>
        )}
      </div>

      <p className="text-sm text-white mb-3">{getStatusText()}</p>

      {scan.status === 'running' && (
        <div className="relative h-2 bg-white/10 rounded-full overflow-hidden">
          <div 
            className="scan-progress-bar absolute top-0 left-0 h-full bg-skyblue rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {scan.status === 'completed' && scan.total_results !== undefined && (
        <div className="mt-3 pt-3 border-t border-white/10 text-xs text-grey">
          <div className="flex justify-between">
            <span>Results Found:</span>
            <span className="text-white font-bold">{scan.total_results}</span>
          </div>
          <div className="flex justify-between mt-1">
            <span>Credentials:</span>
            <span className="text-orange font-bold">{scan.credentials_found || 0}</span>
          </div>
        </div>
      )}

      {/* View Logs Button - Show for completed or failed scans */}
      {(scan.status === 'completed' || scan.status === 'failed') && onViewLogs && (
        <button
          onClick={() => onViewLogs(scan)}
          className="mt-3 w-full bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2 text-sm font-bold"
        >
          <FileText size={16} />
          View Full Logs
        </button>
      )}
    </div>
  );
};

export default ScanNotification;
