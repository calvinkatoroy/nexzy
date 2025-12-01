import React, { useRef } from 'react';
import { useMagnetic } from '../../hooks/useMagnetic';

const MagneticButton = ({ children, onClick, className = "" }) => {
  const btnRef = useRef(null);
  useMagnetic(btnRef);

  return (
    <button
      ref={btnRef}
      onClick={onClick}
      className={`relative px-8 py-4 rounded-full bg-white text-background font-bold text-lg uppercase tracking-wider overflow-hidden group hover:scale-110 transition-transform duration-300 ${className}`}
    >
      {/* Hover Fill Effect */}
      <span className="absolute inset-0 bg-skyblue translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out rounded-full" />
      
      {/* Content */}
      <span className="relative z-10 group-hover:text-white transition-colors duration-300 flex items-center gap-2">
        {children}
      </span>
    </button>
  );
};

export default MagneticButton;