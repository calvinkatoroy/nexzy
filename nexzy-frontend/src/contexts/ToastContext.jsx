import React, { createContext, useContext, useState } from 'react';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';

const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeToast(id);
    }, 5000);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const toast = {
    success: (message) => addToast(message, 'success'),
    error: (message) => addToast(message, 'error'),
    info: (message) => addToast(message, 'info'),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      
      {/* Toast Container */}
      <div className="fixed bottom-4 right-4 z-[200] space-y-2 pointer-events-none">
        {toasts.map(({ id, message, type }) => (
          <Toast key={id} message={message} type={type} onClose={() => removeToast(id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
};

const Toast = ({ message, type, onClose }) => {
  const icons = {
    success: <CheckCircle size={20} className="text-green" />,
    error: <AlertCircle size={20} className="text-red" />,
    info: <Info size={20} className="text-skyblue" />,
  };

  const colors = {
    success: 'border-green/30 bg-green/10',
    error: 'border-red/30 bg-red/10',
    info: 'border-skyblue/30 bg-skyblue/10',
  };

  return (
    <div 
      className={`glass-panel pointer-events-auto border ${colors[type]} rounded-lg p-4 pr-12 min-w-[300px] max-w-md animate-in slide-in-from-right-5 fade-in duration-300`}
    >
      <div className="flex items-start gap-3">
        {icons[type]}
        <p className="text-white text-sm flex-1">{message}</p>
        <button 
          onClick={onClose}
          className="absolute top-2 right-2 p-1 hover:bg-white/10 rounded text-grey hover:text-white transition-colors"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
};
