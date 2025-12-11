import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { animate, stagger } from 'animejs';
import { ArrowRight, Terminal, Shield, Zap, Target, ChevronDown, Github, Code, Database } from 'lucide-react';
import MagneticButton from '../components/common/MagneticButton';
import { useAuth } from '../contexts/AuthContext';

const Landing = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    // If already authenticated, go to dashboard
    if (user) {
      navigate('/dashboard');
      return;
    }
    
    // Initial Entrance Animation
    setTimeout(() => {
      animate('.hero-text-char', {
        opacity: [0, 1],
        y: [100, 0],
        delay: stagger(30),
        duration: 800,
        ease: 'outExpo'
      });

      animate('.hero-sub', {
        opacity: [0, 1],
        y: [20, 0],
        delay: 800,
        duration: 800,
        ease: 'outQuad'
      });
    }, 100);
  }, [user, navigate]);

  const handleEnterSystem = () => {
    navigate('/login');
  };

  const scrollToAbout = () => {
    document.getElementById('about-section').scrollIntoView({ behavior: 'smooth' });
  };

  // Helper to split text for animations
  const splitText = (text) => text.split("").map((char, i) => (
    <span key={i} className="hero-text-char inline-block whitespace-pre opacity-0">
      {char}
    </span>
  ));

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      
      {/* Background: Abstract Cyber Grid */}
      <div className="absolute inset-0 z-0 opacity-10">
        <div className="w-full h-full" style={{ backgroundImage: 'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>
      </div>

      {/* Navigation (Minimal) */}
      <nav className="relative z-10 p-8 flex justify-between items-center">
        <div className="flex items-center gap-2 text-white font-mono text-xl font-bold">
          <Terminal className="text-red" />
          NEXZY<span className="text-grey">.AI</span>
        </div>
        <div className="flex items-center gap-6">
          <button 
            onClick={scrollToAbout}
            className="text-sm text-grey hover:text-white transition-colors font-mono"
          >
            ABOUT
          </button>
          <div className="text-xs text-grey font-mono hidden md:block">
            SECURE CONNECTION // ENCRYPTED
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="min-h-screen flex flex-col justify-center items-center text-center relative z-10 px-4">
        
        {/* Giant Typography */}
        <h1 className="text-[12vw] leading-none font-bold text-white tracking-tighter mb-4">
          {splitText("INTELLIGENCE")}
        </h1>
        
        <h1 className="text-[12vw] leading-none font-bold text-transparent stroke-text tracking-tighter mb-12 relative">
          <span className="absolute inset-0 text-red opacity-50 blur-lg">{splitText("REDEFINED")}</span>
          <span className="relative text-stroke-white">{splitText("REDEFINED")}</span>
        </h1>

        <p className="hero-sub opacity-0 text-grey text-lg md:text-xl max-w-xl mb-12 font-mono leading-relaxed">
          The next generation of automated breach detection. <br/>
          <span className="text-white">Proactive. Invisible. Absolute.</span>
        </p>

        {/* The Magnetic Interaction */}
        <div className="hero-sub opacity-0">
          <MagneticButton onClick={handleEnterSystem}>
            INITIALIZE SYSTEM <ArrowRight size={20} />
          </MagneticButton>
        </div>

        {/* Scroll Indicator */}
        <button 
          onClick={scrollToAbout}
          className="hero-sub opacity-0 absolute bottom-12 animate-bounce text-grey hover:text-white transition-colors"
        >
          <ChevronDown size={32} />
        </button>

      </section>

      {/* About Section (Simplified) */}
      <section id="about-section" className="relative z-10 min-h-screen bg-gradient-to-b from-background to-black/50 border-t border-white/10 flex items-center justify-center">
        
        <div className="max-w-4xl mx-auto px-8 py-20 text-center">
          
          <h2 className="text-5xl md:text-7xl font-bold text-white mb-8">
            Built for <span className="text-transparent bg-clip-text bg-gradient-to-r from-red via-orange to-red">Security</span>
          </h2>
          
          <p className="text-grey text-lg md:text-xl max-w-2xl mx-auto font-mono mb-12 leading-relaxed">
            Advanced OSINT platform for automated threat detection. 
            Real-time monitoring, intelligent analysis, actionable insights.
          </p>

          {/* Key Features - Minimal */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="glass-panel p-6 rounded-xl border border-white/10 hover:border-red/30 transition-all">
              <Zap className="text-red mx-auto mb-3" size={32} />
              <h3 className="text-lg font-bold text-white">Real-Time</h3>
            </div>
            <div className="glass-panel p-6 rounded-xl border border-white/10 hover:border-orange/30 transition-all">
              <Target className="text-orange mx-auto mb-3" size={32} />
              <h3 className="text-lg font-bold text-white">AI-Powered</h3>
            </div>
            <div className="glass-panel p-6 rounded-xl border border-white/10 hover:border-skyblue/30 transition-all">
              <Shield className="text-skyblue mx-auto mb-3" size={32} />
              <h3 className="text-lg font-bold text-white">Automated</h3>
            </div>
          </div>

          {/* CTA */}
          <div className="glass-panel p-8 rounded-xl border border-white/10">
            <p className="text-grey text-sm mb-4 font-mono">GROUP 4 // UNIVERSITAS INDONESIA</p>
            <a 
              href="https://github.com/calvinkatoroy/nexzy" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white transition-all"
            >
              <Github size={20} />
              View Source Code
            </a>
          </div>

        </div>

      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 bg-background/50 backdrop-blur-sm p-4">
        <div className="flex justify-between items-center text-[10px] text-grey font-mono uppercase tracking-widest">
          <span>(C) 2025 NEXZY GROUP 4</span>
          <span className="animate-pulse text-green">● SYSTEM OPERATIONAL</span>
          <span>JAKARTA, ID</span>
        </div>
      </footer>

      {/* CSS for Outline Text */}
      <style>{`
        .text-stroke-white {
          -webkit-text-stroke: 2px rgba(255, 255, 255, 0.8);
          color: transparent;
        }
      `}</style>
    </div>
  );
};

export default Landing;