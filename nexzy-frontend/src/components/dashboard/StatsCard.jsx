import React, { useEffect, useRef } from 'react';
import { animate } from 'animejs';

const StatsCard = ({ title, value, icon: Icon, color, trend }) => {
  const valueRef = useRef(null);

  useEffect(() => {
    // 1. Animate the number counting up
    let obj = { count: 0 };
    animate(obj, {
      count: value,
      round: 1, // Snap to integers
      duration: 1500,
      ease: 'outExpo',
      update: () => {
        if (valueRef.current) valueRef.current.innerText = obj.count;
      }
    });
  }, [value]);

  return (
    <div className={`glass-panel p-6 rounded-2xl relative overflow-hidden group hover:bg-white/5 transition-colors border-l-4 ${color.replace('text-', 'border-')}`}>
      {/* Background Gradient Blob */}
      <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full ${color.replace('text-', 'bg-')} opacity-10 blur-2xl group-hover:opacity-20 transition-opacity`} />

      <div className="flex justify-between items-start mb-4">
        <h3 className="text-grey text-xs uppercase tracking-widest">{title}</h3>
        <div className={`p-2 rounded-lg bg-white/5 ${color}`}>
          <Icon size={20} />
        </div>
      </div>

      <div className="flex items-end gap-3">
        <span ref={valueRef} className="text-4xl font-mono font-bold text-white">0</span>
        {trend && (
          <span className="text-xs mb-1.5 font-mono opacity-60">
            {trend}
          </span>
        )}
      </div>
    </div>
  );
};

export default StatsCard;