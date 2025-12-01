import React, { useEffect, useState } from 'react';
import { animate, svg } from 'animejs';
import { api } from '../../lib/api';

const TrendGraph = () => {
  const [graphData, setGraphData] = useState(null);
  useEffect(() => {
    const loadGraphData = async () => {
      try {
        const alerts = await api.getAlerts();
        
        // Group alerts by day for the last 7 days
        const last7Days = Array.from({ length: 7 }, (_, i) => {
          const date = new Date();
          date.setDate(date.getDate() - (6 - i));
          date.setHours(0, 0, 0, 0);
          return date;
        });
        
        const dailyCounts = last7Days.map(day => {
          const nextDay = new Date(day);
          nextDay.setDate(nextDay.getDate() + 1);
          
          const dayAlerts = alerts.filter(a => {
            const alertDate = new Date(a.created_at);
            return alertDate >= day && alertDate < nextDay;
          });
          
          return {
            date: day,
            alertCount: dayAlerts.length,
            credentialCount: dayAlerts.reduce((sum, a) => {
              const match = a.description.match(/(\d+) records/);
              return sum + (match ? parseInt(match[1]) : 5);
            }, 0)
          };
        });
        
        console.log('[GRAPH] Daily counts:', dailyCounts);
        setGraphData(dailyCounts);
      } catch (err) {
        console.error('Failed to load graph data:', err);
        // Set empty data to still show the graph
        setGraphData(Array(7).fill({ alertCount: 0, credentialCount: 0 }));
      }
    };
    
    loadGraphData();
  }, []);

  useEffect(() => {
    if (!graphData) return;
    
    // 1. Line Drawing Animation
    animate(svg.createDrawable('.trend-line'), {
      draw: '0 1',
      duration: 2000,
      ease: 'outSine',
      delay: 500
    });

    // 2. Fade in the Area fill
    animate('.trend-area', {
      opacity: [0, 0.5],
      duration: 1000,
      delay: 1500,
      ease: 'linear'
    });

    // 3. Animate the dots
    animate('.trend-dot', {
      scale: [0, 1],
      opacity: [0, 1],
      delay: 2000,
      ease: 'outElastic(1, .5)'
    });
  }, [graphData]);

  // Generate dynamic graph paths from real data
  const generatePath = (data, valueKey, maxValue) => {
    if (!data || data.length === 0) return '';
    
    const width = 800;
    const height = 300;
    const padding = 50;
    const stepX = (width - padding * 2) / (data.length - 1);
    
    const points = data.map((d, i) => {
      const x = padding + (i * stepX);
      // Invert Y (0 at bottom) and scale based on max value
      const value = d[valueKey] || 0;
      const y = height - padding - ((value / (maxValue || 1)) * (height - padding * 2));
      return { x, y };
    });
    
    // Create smooth curve path
    let path = `M${points[0].x},${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1];
      const curr = points[i];
      const cpX = prev.x + (curr.x - prev.x) / 2;
      path += ` C${cpX},${prev.y} ${cpX},${curr.y} ${curr.x},${curr.y}`;
    }
    
    return { path, points };
  };

  const maxCredentials = graphData ? Math.max(...graphData.map(d => d.credentialCount || 0), 1) : 1;
  const maxAlerts = graphData ? Math.max(...graphData.map(d => d.alertCount || 0), 1) : 1;
  
  const credPath = graphData ? generatePath(graphData, 'credentialCount', maxCredentials) : { path: '', points: [] };
  const alertPath = graphData ? generatePath(graphData, 'alertCount', maxAlerts) : { path: '', points: [] };

  return (
    <div className="glass-panel p-6 rounded-2xl col-span-1 lg:col-span-2 relative">
      <h3 className="text-white font-bold mb-6 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-red animate-pulse" />
        7-Day Threat Trend
      </h3>
      
      <div className="w-full h-64 relative">
        {graphData ? (
          <svg viewBox="0 0 800 300" className="w-full h-full overflow-visible">
            <defs>
              <linearGradient id="gradientRed" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#FF4B4B" stopOpacity="0.5" />
                <stop offset="100%" stopColor="#FF4B4B" stopOpacity="0" />
              </linearGradient>
              <linearGradient id="gradientBlue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#61C3FF" stopOpacity="0.5" />
                <stop offset="100%" stopColor="#61C3FF" stopOpacity="0" />
              </linearGradient>
            </defs>

            {/* Grid Lines */}
            {[50, 150, 250].map((y, i) => (
              <line key={i} x1="0" y1={y} x2="800" y2={y} stroke="rgba(255,255,255,0.05)" strokeDasharray="4 4" />
            ))}

            {/* Credentials Line (Red) */}
            {credPath.path && (
              <>
                <path 
                  className="trend-area"
                  d={`${credPath.path} L800,300 L50,300 Z`}
                  fill="url(#gradientRed)" 
                  opacity="0"
                />
                <path 
                  className="trend-line"
                  d={credPath.path}
                  fill="none" 
                  stroke="#FF4B4B" 
                  strokeWidth="3" 
                  strokeLinecap="round"
                />
                {credPath.points.map((point, i) => (
                  <circle 
                    key={`cred-${i}`} 
                    cx={point.x} 
                    cy={point.y} 
                    r="4" 
                    fill="#252423" 
                    stroke="#FF4B4B" 
                    strokeWidth="2" 
                    className="trend-dot" 
                  />
                ))}
              </>
            )}

            {/* Alerts Line (Blue) */}
            {alertPath.path && (
              <>
                <path 
                  className="trend-area"
                  d={`${alertPath.path} L800,300 L50,300 Z`}
                  fill="url(#gradientBlue)" 
                  opacity="0"
                />
                <path 
                  className="trend-line"
                  d={alertPath.path}
                  fill="none" 
                  stroke="#61C3FF" 
                  strokeWidth="3" 
                  strokeLinecap="round"
                />
              </>
            )}
          </svg>
        ) : (
          <div className="flex items-center justify-center h-full text-grey">
            Loading graph data...
          </div>
        )}

        {/* Legend */}
        <div className="absolute top-0 right-0 flex gap-4 text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="w-3 h-1 bg-red rounded-full" /> Credentials
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-1 bg-skyblue rounded-full" /> Alerts
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrendGraph;