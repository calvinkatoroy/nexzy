import React from 'react';
import { Shield, Eye, Wifi } from 'lucide-react';

/**
 * DarkWebBadge - Shows dark web monitoring status with animated threat level
 * 
 * Props:
 * - threatLevel: 'safe' | 'elevated' | 'high' | 'critical'
 * - isScanning: boolean - shows animated scanning state
 * - darkWebAlerts: number - count of dark web threats detected
 */
const DarkWebBadge = ({ threatLevel = 'safe', isScanning = false, darkWebAlerts = 0 }) => {
  const levelConfig = {
    safe: {
      color: 'green',
      label: 'Safe',
      icon: Shield,
      gradient: 'from-green/20 to-green/5',
      border: 'border-green/30',
      text: 'text-green'
    },
    elevated: {
      color: 'yellow',
      label: 'Elevated',
      icon: Eye,
      gradient: 'from-yellow/20 to-yellow/5',
      border: 'border-yellow/30',
      text: 'text-yellow'
    },
    high: {
      color: 'orange',
      label: 'High',
      icon: Wifi,
      gradient: 'from-orange/20 to-orange/5',
      border: 'border-orange/30',
      text: 'text-orange'
    },
    critical: {
      color: 'red',
      label: 'Critical',
      icon: Shield,
      gradient: 'from-red/20 to-red/5',
      border: 'border-red/30',
      text: 'text-red'
    }
  };

  const config = levelConfig[threatLevel];
  const Icon = config.icon;

  return (
    <div className={`glass-panel p-4 rounded-xl border ${config.border} bg-gradient-to-br ${config.gradient} relative overflow-hidden`}>
      {/* Animated scanning effect */}
      {isScanning && (
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-scanning" 
             style={{ animation: 'scanning 2s linear infinite' }} />
      )}
      
      <div className="relative z-10 flex items-center gap-3">
        {/* Icon with pulse */}
        <div className={`p-2 rounded-lg bg-${config.color}/10 border border-${config.color}/20 relative`}>
          <Icon className={`${config.text} ${isScanning ? 'animate-pulse' : ''}`} size={20} />
          {isScanning && (
            <div className={`absolute inset-0 rounded-lg bg-${config.color}/20 animate-ping`} />
          )}
        </div>
        
        {/* Status text */}
        <div className="flex-1">
          <div className="text-xs text-grey font-mono uppercase tracking-wider mb-1">
            {isScanning ? 'Scanning Dark Web...' : 'Dark Web Status'}
          </div>
          <div className={`text-sm font-bold ${config.text}`}>
            {config.label}
            {darkWebAlerts > 0 && (
              <span className="ml-2 text-xs text-grey">
                ({darkWebAlerts} threat{darkWebAlerts !== 1 ? 's' : ''})
              </span>
            )}
          </div>
        </div>
        
        {/* Threat level indicator */}
        <div className="flex flex-col gap-1">
          {['critical', 'high', 'elevated', 'safe'].map((level, idx) => (
            <div
              key={level}
              className={`w-8 h-1 rounded-full transition-all ${
                levelConfig[threatLevel].label.toLowerCase() === level.toLowerCase() ||
                (threatLevel === 'critical' && idx === 0) ||
                (threatLevel === 'high' && idx <= 1) ||
                (threatLevel === 'elevated' && idx <= 2) ||
                (threatLevel === 'safe' && idx <= 3)
                  ? `bg-${levelConfig[level].color}`
                  : 'bg-white/10'
              }`}
            />
          ))}
        </div>
      </div>
      
      {/* Pulsing glow effect for critical */}
      {threatLevel === 'critical' && (
        <div className="absolute -inset-4 bg-red/10 blur-2xl animate-pulse pointer-events-none" />
      )}
    </div>
  );
};

export default DarkWebBadge;

// Add to tailwind.config.js animations:
// animation: {
//   scanning: 'scanning 2s linear infinite',
// },
// keyframes: {
//   scanning: {
//     '0%': { transform: 'translateX(-100%)' },
//     '100%': { transform: 'translateX(100%)' },
//   },
// }
