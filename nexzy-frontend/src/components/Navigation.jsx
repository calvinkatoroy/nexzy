import React, { useEffect, useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Search, Bell, Settings, TerminalSquare, LogOut } from 'lucide-react';
import { animate, stagger } from 'animejs';
import { useAuth } from '../contexts/AuthContext';

// Configuration for our navigation items
const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard', color: 'text-red' },
  { icon: Search, label: 'Intelligence', path: '/search', color: 'text-skyblue' },
  { icon: TerminalSquare, label: 'Command', action: 'CMD_K', color: 'text-green' }, // Special Trigger
  { icon: Bell, label: 'Alerts', path: '/alerts', color: 'text-orange' },
  { icon: Settings, label: 'Settings', path: '/settings', color: 'text-grey' },
  { icon: LogOut, label: 'Log Out', action: 'LOGOUT', color: 'text-red' }, // Logout button
];

const Navigation = ({ onCommandClick }) => {
  const dockRef = useRef(null);
  const navigate = useNavigate();
  const { signOut } = useAuth();

  const handleLogout = async () => {
    try {
      // Proper logout using auth context
      await signOut();
      // Clear any additional local storage
      localStorage.clear();
      sessionStorage.clear();
      // Redirect to landing page
      navigate('/landing');
    } catch (error) {
      console.error('Logout error:', error);
      // Force redirect even if error
      navigate('/landing');
    }
  };

  useEffect(() => {
    // 1. Anime.js v4 Entrance Animation
    // The dock slides in from a subtle offset with a springy elasticity
    animate(dockRef.current, {
      opacity: [0, 1],
      x: ['-20px', '0px'], // Start slightly off-screen (desktop)
      y: ['20px', '0px'],  // Start slightly down (mobile)
      duration: 1000,
      ease: 'spring(1, 80, 10, 0)'
    });

    // 2. Staggered Icon Entry
    // The icons fade in one by one after the dock appears
    animate('.nav-item', {
      opacity: [0, 1],
      scale: [0.5, 1],
      delay: stagger(100, { start: 200 }),
      ease: 'spring(1, 80, 10, 0)'
    });
  }, []);

  return (
    <>
      {/* Container Positioning:
        - Mobile: Fixed bottom, centered horizontally
        - Desktop (md): Fixed left, centered vertically
      */}
      <nav 
        ref={dockRef}
        className="fixed z-50 
          bottom-6 left-1/2 -translate-x-1/2 w-auto h-16 
          md:left-6 md:top-1/2 md:-translate-y-1/2 md:w-16 md:h-auto md:translate-x-0
          flex items-center justify-center"
      >
        {/* The Glass Pill */}
        <div className="glass-panel rounded-full px-6 py-3 md:px-3 md:py-6 flex md:flex-col items-center gap-6 shadow-2xl">
          
          {NAV_ITEMS.map((item, index) => {
            const Icon = item.icon;
            
            // Render logic: specific styling if it's a "Command" button vs a Link
            if (item.action) {
              const handleClick = item.action === 'LOGOUT' ? handleLogout : onCommandClick;
              
              return (
                <button
                  key={index}
                  onClick={handleClick}
                  className={`nav-item group relative p-2 rounded-xl transition-all duration-300 hover:bg-white/5 hover:scale-125`}
                  title={item.label}
                >
                  <Icon className={`w-6 h-6 ${item.color} transition-colors`} />
                  {/* Tooltip for Desktop */}
                  <span className="absolute left-14 top-1/2 -translate-y-1/2 bg-background border border-white/10 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap hidden md:block pointer-events-none">
                    {item.label} {item.action === 'CMD_K' && <span className="text-grey font-mono text-[10px]">⌘K</span>}
                  </span>
                </button>
              );
            }

            return (
              <NavLink
                key={index}
                to={item.path}
                className={({ isActive }) => `
                  nav-item group relative p-2 rounded-xl transition-all duration-300 hover:scale-125
                  ${isActive ? 'bg-white/10 shadow-[0_0_15px_rgba(255,255,255,0.1)]' : 'hover:bg-white/5'}
                `}
              >
                <Icon className={`w-6 h-6 ${item.color}`} />
                
                {/* Active Indicator Dot (Apple Style) */}
                <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-white rounded-full opacity-0 aria-[current=page]:opacity-100 md:bottom-auto md:left-auto md:top-1/2 md:-right-2 md:-translate-y-1/2" aria-current={window.location.pathname === item.path ? 'page' : undefined} />
                
                {/* Tooltip */}
                <span className="absolute left-14 top-1/2 -translate-y-1/2 bg-background border border-white/10 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap hidden md:block pointer-events-none">
                  {item.label}
                </span>
              </NavLink>
            );
          })}
        </div>
      </nav>
    </>
  );
};

export default Navigation;