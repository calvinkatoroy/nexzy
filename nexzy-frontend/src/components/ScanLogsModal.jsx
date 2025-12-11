import React from 'react';
import { X, FileText, AlertTriangle, Info, CheckCircle } from 'lucide-react';

const ScanLogsModal = ({ scan, logs, onClose }) => {
  if (!scan) return null;

  const getLevelIcon = (level) => {
    switch (level) {
      case 'ERROR':
        return <AlertTriangle size={14} className="text-red" />;
      case 'WARNING':
        return <AlertTriangle size={14} className="text-orange" />;
      case 'SUCCESS':
        return <CheckCircle size={14} className="text-green" />;
      default:
        return <Info size={14} className="text-skyblue" />;
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'ERROR':
        return 'text-red';
      case 'WARNING':
        return 'text-orange';
      case 'SUCCESS':
        return 'text-green';
      default:
        return 'text-grey';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in">
      <div className="glass-panel w-full max-w-4xl max-h-[80vh] m-6 rounded-xl border border-skyblue/30 shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <FileText size={24} className="text-skyblue" />
            <div>
              <h2 className="text-xl font-bold text-white">Scan Logs</h2>
              <p className="text-xs text-grey font-mono mt-1">
                Scan ID: {scan.scan_id || scan.id}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-grey hover:text-white transition-colors p-2 hover:bg-white/5 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        {/* Scan Summary */}
        <div className="px-6 py-4 border-b border-white/10 bg-white/5">
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-grey text-xs">Status</p>
              <p className={`font-bold ${
                scan.status === 'completed' ? 'text-green' :
                scan.status === 'failed' ? 'text-red' :
                'text-orange'
              }`}>
                {scan.status?.toUpperCase()}
              </p>
            </div>
            <div>
              <p className="text-grey text-xs">Progress</p>
              <p className="font-bold text-white">{Math.round((scan.progress || 0) * 100)}%</p>
            </div>
            <div>
              <p className="text-grey text-xs">Results Found</p>
              <p className="font-bold text-skyblue">{scan.total_results || 0}</p>
            </div>
            <div>
              <p className="text-grey text-xs">Credentials</p>
              <p className="font-bold text-orange">{scan.credentials_found || 0}</p>
            </div>
          </div>
        </div>

        {/* Logs Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-2 font-mono text-xs">
          {logs && logs.length > 0 ? (
            logs.map((log, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-2 hover:bg-white/5 rounded transition-colors"
              >
                <span className="text-grey flex-shrink-0">{formatTimestamp(log.timestamp)}</span>
                <span className="flex-shrink-0">{getLevelIcon(log.level)}</span>
                <span className={`${getLevelColor(log.level)} flex-1`}>{log.message}</span>
              </div>
            ))
          ) : (
            <div className="text-center py-12 text-grey">
              <FileText size={48} className="mx-auto mb-4 opacity-30" />
              <p>No logs available for this scan</p>
              <p className="text-xs mt-2">Logs are stored during scan execution</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 flex justify-end gap-3">
          <button
            onClick={() => {
              const logsText = logs?.map(log => 
                `[${formatTimestamp(log.timestamp)}] [${log.level}] ${log.message}`
              ).join('\n') || 'No logs available';
              
              const blob = new Blob([logsText], { type: 'text/plain' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `scan-${scan.scan_id || scan.id}-logs.txt`;
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              URL.revokeObjectURL(url);
            }}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors font-bold text-sm"
          >
            Download Logs
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-skyblue hover:bg-white text-black rounded-lg transition-colors font-bold text-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ScanLogsModal;
