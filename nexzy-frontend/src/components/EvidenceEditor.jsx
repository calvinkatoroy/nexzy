import React, { useEffect, useRef } from 'react';
import { Copy, Terminal } from 'lucide-react';
import { animate, stagger } from 'animejs';

const EvidenceEditor = ({ content, filename = "dump.txt" }) => {
  const containerRef = useRef(null);

  // Simple Regex to highlight sensitive data for that "Hacker" look
  const highlightCode = (text) => {
    // Emails -> Red
    let processed = text.replace(
      /([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})/g,
      '<span class="text-red">$1</span>'
    );
    // IPs -> Blue
    processed = processed.replace(
      /(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)/g,
      '<span class="text-skyblue">$1</span>'
    );
    // Key/Value separators (e.g., "Password:") -> Lavender
    processed = processed.replace(
      /([a-zA-Z0-9-_]+[:=])/g,
      '<span class="text-lavender">$1</span>'
    );
    return processed;
  };

  useEffect(() => {
    // Anime.js v4 Stagger Syntax
    // Animates each line sliding in from the left
    animate('.code-line', {
      opacity: [0, 1],
      x: [-20, 0], 
      delay: stagger(30, { start: 200 }),
      ease: 'outExpo'
    });
  }, [content]);

  return (
    <div ref={containerRef} className="glass-panel rounded-lg overflow-hidden flex flex-col font-mono text-sm shadow-2xl my-6">
      
      {/* Editor Toolbar */}
      <div className="bg-white/5 border-b border-white/10 px-4 py-2 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Terminal size={14} className="text-grey" />
          <span className="text-grey text-xs">{filename}</span>
        </div>
        <button 
          className="flex items-center gap-2 text-xs text-grey hover:text-white transition-colors"
          onClick={() => navigator.clipboard.writeText(content)}
        >
          <Copy size={14} />
          <span>COPY RAW</span>
        </button>
      </div>

      {/* Code Area */}
      <div className="p-4 overflow-x-auto bg-[#1e1e1e]/50">
        <pre className="font-mono text-xs md:text-sm leading-relaxed">
          {content.split('\n').map((line, i) => (
            <div key={i} className="code-line flex opacity-0">
              {/* Line Number */}
              <span className="w-8 text-grey/30 select-none text-right mr-4">{i + 1}</span>
              {/* Content */}
              <span 
                className="text-white/90"
                dangerouslySetInnerHTML={{ __html: highlightCode(line) || ' ' }} 
              />
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
};

export default EvidenceEditor;