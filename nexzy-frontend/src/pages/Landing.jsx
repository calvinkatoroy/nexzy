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

      {/* About/Info Section */}
      <section id="about-section" className="relative z-10 min-h-screen bg-gradient-to-b from-background to-black/50 border-t border-white/10">
        
        <div className="max-w-7xl mx-auto px-8 py-20">
          
          {/* Section Header */}
          <div className="text-center mb-20">
            <p className="text-red font-mono text-sm mb-4 tracking-widest">ABOUT THE PROJECT</p>
            <h2 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Proactive Threat <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-red via-orange to-red">Intelligence</span>
            </h2>
            <p className="text-grey text-lg max-w-2xl mx-auto font-mono">
              Nexzy monitors unstructured data sources in real-time to detect potential security breaches before they escalate.
            </p>
          </div>

          {/* Key Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-20">
            
            {/* Feature 1 */}
            <div className="glass-panel p-8 rounded-xl border border-white/10 hover:border-red/30 transition-all group">
              <div className="w-12 h-12 bg-red/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-red/20 transition-colors">
                <Zap className="text-red" size={24} />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Real-Time Monitoring</h3>
              <p className="text-grey text-sm leading-relaxed">
                Automated scraping of paste sites like Pastebin with keyword-based targeting for instant breach detection.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="glass-panel p-8 rounded-xl border border-white/10 hover:border-orange/30 transition-all group">
              <div className="w-12 h-12 bg-orange/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-orange/20 transition-colors">
                <Target className="text-orange" size={24} />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Smart Analysis</h3>
              <p className="text-grey text-sm leading-relaxed">
                AI-powered risk scoring and automatic summarization to prioritize critical threats and reduce noise.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="glass-panel p-8 rounded-xl border border-white/10 hover:border-skyblue/30 transition-all group">
              <div className="w-12 h-12 bg-skyblue/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-skyblue/20 transition-colors">
                <Shield className="text-skyblue" size={24} />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Actionable Alerts</h3>
              <p className="text-grey text-sm leading-relaxed">
                Structured dashboard with filtering, search, and export capabilities for rapid incident response.
              </p>
            </div>

          </div>

          {/* Architecture Section */}
          <div className="glass-panel p-12 rounded-xl border border-white/10 mb-20">
            <h3 className="text-3xl font-bold text-white mb-8 text-center">System Architecture</h3>
            
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              
              {/* Frontend */}
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-skyblue/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Code className="text-skyblue" size={32} />
                </div>
                <h4 className="text-xl font-bold text-white mb-2">Frontend</h4>
                <p className="text-grey text-sm mb-3">React + Vite</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">React Router</span>
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">Tailwind CSS</span>
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">Anime.js</span>
                </div>
              </div>

              {/* Arrow */}
              <div className="text-grey">
                <ArrowRight size={32} className="hidden md:block" />
                <ChevronDown size={32} className="md:hidden" />
              </div>

              {/* Backend */}
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-red/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Terminal className="text-red" size={32} />
                </div>
                <h4 className="text-xl font-bold text-white mb-2">Backend</h4>
                <p className="text-grey text-sm mb-3">Python + FastAPI</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">BeautifulSoup</span>
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">WebSockets</span>
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">Uvicorn</span>
                </div>
              </div>

              {/* Arrow */}
              <div className="text-grey">
                <ArrowRight size={32} className="hidden md:block" />
                <ChevronDown size={32} className="md:hidden" />
              </div>

              {/* Database */}
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-green/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Database className="text-green" size={32} />
                </div>
                <h4 className="text-xl font-bold text-white mb-2">Database</h4>
                <p className="text-grey text-sm mb-3">Supabase</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">PostgreSQL</span>
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">Auth</span>
                  <span className="px-3 py-1 bg-white/5 rounded text-xs text-grey border border-white/10">Real-time</span>
                </div>
              </div>

            </div>
          </div>

          {/* Stats/Highlights */}
          <div className="grid md:grid-cols-4 gap-6 mb-20">
            <div className="text-center">
              <div className="text-4xl font-bold text-red mb-2">100%</div>
              <div className="text-grey text-sm font-mono">Automated</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-orange mb-2">&lt;3s</div>
              <div className="text-grey text-sm font-mono">Detection Time</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-skyblue mb-2">24/7</div>
              <div className="text-grey text-sm font-mono">Monitoring</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green mb-2">∞</div>
              <div className="text-grey text-sm font-mono">Sources</div>
            </div>
          </div>

          {/* Team/Project Info */}
          <div className="glass-panel p-12 rounded-xl border border-white/10 text-center">
            <h3 className="text-2xl font-bold text-white mb-4">Built by Group 4</h3>
            <p className="text-grey mb-8 max-w-2xl mx-auto">
              Nexzy is an academic research project focused on proactive cybersecurity threat detection, 
              developed as part of advanced security coursework at Universitas Indonesia.
            </p>
            <a 
              href="https://github.com/calvinkatoroy/nexzy" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white transition-all"
            >
              <Github size={20} />
              View on GitHub
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