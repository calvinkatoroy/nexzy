import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { animate, stagger, createTimeline } from 'animejs';
import { ShieldCheck, Lock, ChevronRight, Fingerprint, UserPlus, ArrowLeft, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { signIn, signUp, user } = useAuth();
  
  // Stages: boot -> selection -> login_form OR register_form -> scanning -> success
  const [stage, setStage] = useState('boot'); 
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  
  // Form States
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [regForm, setRegForm] = useState({ codename: '', email: '', password: '', clearance: 'Level 1' });
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Redirect if already logged in
  useEffect(() => {
    if (user) navigate('/dashboard');
  }, [user, navigate]);

  // Refs
  const terminalRef = useRef(null);
  const containerRef = useRef(null);
  const scanRef = useRef(null);

  // 1. INITIAL BOOT SEQUENCE
  useEffect(() => {
    const bootSequence = async () => {
      await animate('.boot-line', {
        opacity: [0, 1],
        x: [-20, 0],
        delay: stagger(100),
        duration: 500,
        ease: 'outMono', // Custom easing defined in tailwind/css or fallback
      }).finished;

      setTimeout(() => setStage('selection'), 800);
    };
    bootSequence();
  }, []);

  // 2. MODE SWITCH ANIMATION (Login <-> Register)
  useEffect(() => {
    if (stage === 'form') {
      // Animate Container Resize & Content Fade In
      animate(containerRef.current, {
        scale: [0.95, 1],
        opacity: [0, 1],
        duration: 600,
        ease: 'outExpo'
      });
      
      animate('.input-group', {
        opacity: [0, 1],
        y: [20, 0],
        delay: stagger(50, { start: 100 }),
        ease: 'outQuad'
      });
    }
  }, [stage, mode]);

  const switchMode = (newMode) => {
    // Fade out current form
    animate(containerRef.current, {
      opacity: 0,
      scale: 0.95,
      duration: 300,
      ease: 'inQuad',
      onComplete: () => {
        setMode(newMode);
        // Form will re-animate via the useEffect watching stage & mode
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    setStage('scanning');

    try {
      if (mode === 'login') {
        await signIn(loginForm.email, loginForm.password);
      } else {
        await signUp(regForm.email, regForm.password, {
          codename: regForm.codename,
          clearance: regForm.clearance,
        });
      }

      // BIOMETRIC SCAN ANIMATION
      const tl = createTimeline({
        onComplete: () => {
          setStage('success');
          setTimeout(() => navigate('/dashboard'), 1000);
        }
      });

      tl.add(scanRef.current, {
        height: ['0%', '100%'],
        opacity: [0, 0.5, 0],
        duration: 1500,
        ease: 'inOutQuad'
      });
      
      tl.add('.auth-card', {
        borderColor: ['rgba(255,255,255,0.1)', mode === 'login' ? '#18FF74' : '#61C3FF'],
        duration: 500,
      }, '-=500');
    } catch (err) {
      setError(err.message || 'Authentication failed');
      setStage('form');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background p-4 relative overflow-hidden font-mono">
      
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-20 pointer-events-none" 
           style={{ backgroundImage: 'radial-gradient(#b8b6b3 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      {/* STAGE 1: BOOT TERMINAL */}
      {stage === 'boot' && (
        <div ref={terminalRef} className="text-sm max-w-md w-full space-y-2">
          <div className="boot-line text-grey opacity-0">{'>'} NEXZY_KERNEL_V4.1.17... <span className="text-green">OK</span></div>
          <div className="boot-line text-grey opacity-0">{'>'} MOUNTING_SECURITY_MODULES... <span className="text-green">OK</span></div>
          <div className="boot-line text-grey opacity-0">{'>'} ESTABLISHING_SECURE_HANDSHAKE... <span className="text-yellow">WAIT</span></div>
          <div className="boot-line text-skyblue opacity-0">{'>'} INITIALIZING_AUTH_PROTOCOL...</div>
        </div>
      )}

      {/* STAGE 2: SELECTION MENU */}
      {stage === 'selection' && (
        <div className="flex gap-6">
          <button 
            onClick={() => { setMode('login'); setStage('form'); }}
            className="group glass-panel p-8 rounded-2xl hover:bg-white/5 transition-all w-48 flex flex-col items-center gap-4 border border-white/10 hover:border-green"
          >
            <div className="p-4 rounded-full bg-white/5 text-green group-hover:scale-110 transition-transform">
              <Lock size={32} />
            </div>
            <span className="text-white font-bold tracking-wider">LOGIN</span>
          </button>

          <button 
            onClick={() => { setMode('register'); setStage('form'); }}
            className="group glass-panel p-8 rounded-2xl hover:bg-white/5 transition-all w-48 flex flex-col items-center gap-4 border border-white/10 hover:border-skyblue"
          >
            <div className="p-4 rounded-full bg-white/5 text-skyblue group-hover:scale-110 transition-transform">
              <UserPlus size={32} />
            </div>
            <span className="text-white font-bold tracking-wider">REGISTER</span>
          </button>
        </div>
      )}

      {/* STAGE 3, 4, 5: FORM & SCANNING */}
      {(stage === 'form' || stage === 'scanning' || stage === 'success') && (
        <div 
          ref={containerRef} 
          className="auth-card glass-panel w-full max-w-md p-8 rounded-2xl border border-white/10 relative overflow-hidden shadow-2xl"
        >
          {/* Biometric Scanner Overlay */}
          <div ref={scanRef} className={`absolute top-0 left-0 w-full bg-gradient-to-b from-transparent via-${mode === 'login' ? 'green' : 'skyblue'}/20 to-${mode === 'login' ? 'green' : 'skyblue'}/50 border-b-2 border-${mode === 'login' ? 'green' : 'skyblue'} z-20 pointer-events-none h-0 opacity-0`} />

          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <button onClick={() => setStage('selection')} className="text-grey hover:text-white transition-colors">
              <ArrowLeft size={20} />
            </button>
            <div className="text-right">
              <h2 className="text-xl font-bold text-white uppercase">{mode === 'login' ? 'Agent Login' : 'Request Access'}</h2>
              <p className="text-[10px] text-grey uppercase tracking-widest">SECURE CHANNEL</p>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red/10 border border-red/30 rounded-lg p-3 flex items-center gap-2 text-red text-sm">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
            
            {/* REGISTER FIELDS */}
            {mode === 'register' && (
              <>
                <div className="input-group opacity-0 grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-grey ml-1 mb-1 block">CODENAME</label>
                    <input 
                      type="text" 
                      required
                      value={regForm.codename}
                      onChange={(e) => setRegForm({...regForm, codename: e.target.value})}
                      className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-skyblue outline-none" 
                      placeholder="Neo" 
                    />
                  </div>
                  <div>
                    <label className="text-xs text-grey ml-1 mb-1 block">CLEARANCE</label>
                    <select 
                      value={regForm.clearance}
                      onChange={(e) => setRegForm({...regForm, clearance: e.target.value})}
                      className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-skyblue outline-none"
                    >
                      <option>Level 1</option>
                      <option>Level 2</option>
                      <option>Level 3 (Restricted)</option>
                    </select>
                  </div>
                </div>
                <div className="input-group opacity-0">
                  <label className="text-xs text-grey ml-1 mb-1 block">OFFICIAL EMAIL</label>
                  <input 
                    type="email" 
                    required
                    value={regForm.email}
                    onChange={(e) => setRegForm({...regForm, email: e.target.value})}
                    className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-skyblue outline-none" 
                    placeholder="agent@nexzy.ai" 
                  />
                </div>
                <div className="input-group opacity-0">
                  <label className="text-xs text-grey ml-1 mb-1 block">SET PASSWORD</label>
                  <input 
                    type="password" 
                    required
                    value={regForm.password}
                    onChange={(e) => setRegForm({...regForm, password: e.target.value})}
                    className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-skyblue outline-none" 
                    placeholder="••••••••••••" 
                  />
                </div>
              </>
            )}

            {/* LOGIN FIELDS */}
            {mode === 'login' && (
              <>
                <div className="input-group opacity-0">
                  <label className="text-xs text-grey ml-1 mb-1 block">EMAIL</label>
                  <input 
                    type="email"
                    required
                    value={loginForm.email}
                    onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                    className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-green outline-none transition-colors"
                    placeholder="agent@nexzy.ai"
                    autoFocus
                  />
                </div>
                <div className="input-group opacity-0">
                  <label className="text-xs text-grey ml-1 mb-1 block">PASSWORD</label>
                  <input 
                    type="password" 
                    required
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                    className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white focus:border-green outline-none" 
                    placeholder="••••••••••••" 
                  />
                </div>
              </>
            )}

            <button 
              type="submit"
              disabled={stage !== 'form' || isSubmitting}
              className={`input-group opacity-0 w-full font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed ${
                mode === 'login' 
                  ? 'bg-white text-background hover:bg-green hover:text-black' 
                  : 'bg-skyblue text-black hover:bg-white'
              }`}
            >
              {stage === 'scanning' ? (
                <>VERIFYING <Fingerprint className="animate-pulse" size={18} /></>
              ) : (
                <>{mode === 'login' ? 'AUTHENTICATE' : 'SUBMIT REQUEST'} <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" /></>
              )}
            </button>
          </form>

        </div>
      )}
    </div>
  );
};

export default LoginPage;