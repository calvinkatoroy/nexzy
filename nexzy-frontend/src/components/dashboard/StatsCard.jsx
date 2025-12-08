import React, { useEffect, useRef, useState } from 'react';
import { animate } from 'animejs';

const StatsCard = ({ title, value, icon: Icon, color, trend, statKey }) => {
  const valueRef = useRef(null);
  const [fetchedValue, setFetchedValue] = useState(null);

  // Fetch from /api/stats if value is not provided
  useEffect(() => {
    const key = statKey || mapTitleToKey(title);
    if (value === undefined && key) {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      fetch(`/api/stats`, {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      })
        .then((res) => (res.ok ? res.json() : Promise.reject(new Error('Failed to fetch stats'))))
        .then((data) => {
          if (data && Object.prototype.hasOwnProperty.call(data, key)) {
            setFetchedValue(data[key]);
          }
        })
        .catch(() => {
          // Silent fail: keep default 0
        });
    }
  }, [value, title, statKey]);

  // Normalize incoming value to an integer count
  const normalized = (() => {
    try {
      const sourceVal = value !== undefined ? value : fetchedValue;
      if (Array.isArray(sourceVal)) return sourceVal.length;
      if (typeof sourceVal === 'string') {
        const n = parseInt(sourceVal.replace(/[^0-9-]/g, ''), 10);
        return Number.isFinite(n) ? Math.max(0, n) : 0;
      }
      if (typeof sourceVal === 'number') return Math.max(0, Math.round(sourceVal));
      if (typeof sourceVal === 'object' && sourceVal !== null) {
        // Support objects like { count: X }
        const n = parseInt(sourceVal.count, 10);
        return Number.isFinite(n) ? Math.max(0, n) : 0;
      }
      return 0;
    } catch {
      return 0;
    }
  })();

  useEffect(() => {
    const start = (() => {
      const currentText = valueRef.current?.innerText || '0';
      const n = parseInt(currentText.replace(/[^0-9-]/g, ''), 10);
      return Number.isFinite(n) ? n : 0;
    })();

    const obj = { count: start };
    animate(obj, {
      count: normalized,
      round: 1,
      duration: 800,
      ease: 'outExpo',
      update: () => {
        if (valueRef.current) valueRef.current.innerText = obj.count.toLocaleString();
      }
    });
  }, [normalized]);

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

function mapTitleToKey(title) {
  const t = (title || '').toLowerCase();
  if (t.includes('new alert')) return 'new_alerts';
  if (t.includes('credential')) return 'credentials_leaked';
  if (t.includes('critical')) return 'alerts_critical';
  if (t.includes('resolved')) return 'alerts_resolved';
  return null;
}

export default StatsCard;