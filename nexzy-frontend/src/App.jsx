import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, Navigate, useNavigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import SearchPage from './pages/SearchPage';
import AlertDetails from './pages/AlertDetails';
import LoginPage from './pages/Login';
import Landing from './pages/Landing';
import Settings from './pages/Settings';
import AlertsPage from './pages/AlertsPage';
import PageTransition from './components/PageTransition';
import { Search, LayoutDashboard, Bell, Settings as SettingsIcon, LogOut } from 'lucide-react';
import { useAuth } from './contexts/AuthContext';

// The wrapper that decides if sidebar is visible
const AppLayout = ({ children, onCommandClick }) => {
  const location = useLocation();
  // Hide sidebar on Login AND Landing pages
  const isFullScreen = ['/login', '/landing'].includes(location.pathname);

  return (
    <div className="min-h-screen w-full bg-background text-white selection:bg-red/30 font-mono">
      {!isFullScreen && <Navigation onCommandClick={onCommandClick} />}
      <main className={`relative ${!isFullScreen ? 'p-6 pb-24 md:pl-32 md:pt-10 max-w-7xl mx-auto' : ''} min-h-screen`}>
        {/* Wrap Routes in the Transition Component */}
        <PageTransition>
           {children}
        </PageTransition>
      </main>
    </div>
  );
};

function App() {
  const [isCmdOpen, setIsCmdOpen] = useState(false);

  // Listen for Cmd/Ctrl+K
  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCmdOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setIsCmdOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <Router>
      <AppLayout onCommandClick={() => setIsCmdOpen(true)}>
        <Routes>
          <Route path="/" element={<Navigate to="/landing" replace />} />
          <Route path="/landing" element={<Landing />} />
          <Route path="/login" element={<LoginPage />} />          
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/search" element={<ProtectedRoute><SearchPage /></ProtectedRoute>} />
          <Route path="/alerts" element={<ProtectedRoute><AlertsPage /></ProtectedRoute>} />
          <Route path="/alerts/:id" element={<ProtectedRoute><AlertDetails /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/landing" replace />} />
        </Routes>
        
        {/* Command Palette */}
        <CommandPalette isOpen={isCmdOpen} onClose={() => setIsCmdOpen(false)} />

      </AppLayout>
    </Router>
  );
}

// Command Palette Component
const CommandPalette = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const [search, setSearch] = useState('');

  const commands = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard', color: 'text-red' },
    { icon: Search, label: 'Search Intelligence', path: '/search', color: 'text-skyblue' },
    { icon: Bell, label: 'View Alerts', path: '/alerts', color: 'text-orange' },
    { icon: SettingsIcon, label: 'Settings', path: '/settings', color: 'text-grey' },
    { icon: LogOut, label: 'Log Out', action: 'logout', color: 'text-red' },
  ];

  const filteredCommands = commands.filter(cmd => 
    cmd.label.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = async (cmd) => {
    if (cmd.action === 'logout') {
      await signOut();
      navigate('/landing');
    } else {
      navigate(cmd.path);
    }
    onClose();
    setSearch('');
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-start justify-center pt-[20vh] animate-in fade-in duration-200" 
      onClick={onClose}
    >
      <div 
        className="glass-panel w-full max-w-xl rounded-xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200" 
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="flex items-center gap-3 p-4 border-b border-white/10">
          <Search className="w-5 h-5 text-grey" />
          <input
            type="text"
            placeholder="Type a command or search..."
            className="flex-1 bg-transparent text-white placeholder:text-grey outline-none"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
          />
          <kbd className="px-2 py-1 text-xs bg-white/5 rounded border border-white/10 text-grey">ESC</kbd>
        </div>

        {/* Commands List */}
        <div className="max-h-96 overflow-y-auto">
          {filteredCommands.map((cmd, i) => {
            const Icon = cmd.icon;
            return (
              <button
                key={i}
                onClick={() => handleSelect(cmd)}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors text-left group"
              >
                <Icon className={`w-5 h-5 ${cmd.color}`} />
                <span className="text-white group-hover:text-white/90">{cmd.label}</span>
              </button>
            );
          })}
          {filteredCommands.length === 0 && (
            <div className="px-4 py-8 text-center text-grey">No commands found</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;