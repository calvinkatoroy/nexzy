import React, { useRef, useEffect } from 'react';
import { animate } from 'animejs';
import { Filter, X } from 'lucide-react';

const SearchFilters = ({ isOpen, onClose }) => {
  const panelRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      // Slide Down Animation
      animate(panelRef.current, {
        height: ['0px', '180px'],
        opacity: [0, 1],
        duration: 600,
        ease: 'outExpo'
      });
      // Stagger in the options
      animate('.filter-group', {
        opacity: [0, 1],
        y: [-10, 0],
        delay: (el, i) => i * 50 + 100,
        ease: 'outQuad'
      });
    } else {
      // Slide Up Animation
      if (panelRef.current) {
        animate(panelRef.current, {
          height: '0px',
          opacity: 0,
          duration: 400,
          ease: 'outQuad'
        });
      }
    }
  }, [isOpen]);

  return (
    <div ref={panelRef} className="overflow-hidden mb-6 h-0">
      <div className="glass-panel p-4 rounded-xl border border-white/10 grid grid-cols-1 md:grid-cols-4 gap-6 relative">
        
        {/* Close Button for Mobile */}
        <button onClick={onClose} className="absolute top-2 right-2 text-grey hover:text-white md:hidden">
          <X size={16} />
        </button>

        {/* Filter Groups */}
        <div className="filter-group opacity-0">
          <label className="text-xs text-grey uppercase tracking-wider mb-2 block">Source</label>
          <select className="w-full bg-background border border-white/10 rounded px-3 py-2 text-sm text-white focus:border-skyblue outline-none font-mono">
            <option>All Sources</option>
            <option>Pastebin</option>
            <option>GitHub</option>
            <option>Dark Web</option>
          </select>
        </div>

        <div className="filter-group opacity-0">
          <label className="text-xs text-grey uppercase tracking-wider mb-2 block">Severity</label>
          <select className="w-full bg-background border border-white/10 rounded px-3 py-2 text-sm text-white focus:border-red outline-none font-mono">
            <option>Any Severity</option>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
          </select>
        </div>

        <div className="filter-group opacity-0">
          <label className="text-xs text-grey uppercase tracking-wider mb-2 block">Credential Type</label>
          <select className="w-full bg-background border border-white/10 rounded px-3 py-2 text-sm text-white focus:border-lavender outline-none font-mono">
            <option>All Types</option>
            <option>Email/Password</option>
            <option>API Key</option>
            <option>Database String</option>
          </select>
        </div>

        <div className="filter-group opacity-0">
          <label className="text-xs text-grey uppercase tracking-wider mb-2 block">Date Range</label>
          <select className="w-full bg-background border border-white/10 rounded px-3 py-2 text-sm text-white focus:border-green outline-none font-mono">
            <option>Last 24 Hours</option>
            <option>Last 7 Days</option>
            <option>Last 30 Days</option>
          </select>
        </div>

      </div>
    </div>
  );
};

export default SearchFilters;