import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { animate, stagger } from 'animejs';
import { ArrowRight, Terminal } from 'lucide-react';
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
  }, []);

  const handleEnterSystem = () => {
    navigate('/login');
  };

  // Helper to split text for animations
  const splitText = (text) => text.split("").map((char, i) => (
    <span key={i} className="hero-text-char inline-block whitespace-pre opacity-0">
      {char}
    </span>
  ));

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col">
      
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
        <div className="text-xs text-grey font-mono hidden md:block">
          SECURE CONNECTION // ENCRYPTED
        </div>
      </nav>

      {/* Hero Content */}
      <main className="flex-1 flex flex-col justify-center items-center text-center relative z-10 px-4">
        
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

      </main>

      {/* Footer ticker */}
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