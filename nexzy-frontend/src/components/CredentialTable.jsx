import React, { useEffect } from 'react';
import { animate, stagger } from 'animejs';

const CredentialTable = ({ credentials }) => {
  
  useEffect(() => {
    // Anime.js v4 Table Stagger
    animate('.cred-row', {
      opacity: [0, 1],
      y: [10, 0],
      delay: stagger(50, { start: 500 }), // Starts after the editor loads
      ease: 'outQuad'
    });
  }, [credentials]);

  return (
    <div className="w-full overflow-hidden rounded-xl border border-white/10 mt-6">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-white/5 text-xs text-grey uppercase tracking-wider border-b border-white/10">
            <th className="p-4">ID</th>
            <th className="p-4">Type</th>
            <th className="p-4">Email / Username</th>
            <th className="p-4">Domain</th>
            <th className="p-4">Exposure</th>
          </tr>
        </thead>
        <tbody className="font-mono text-sm">
          {credentials.map((cred, idx) => (
            <tr key={idx} className="cred-row border-b border-white/5 hover:bg-white/5 transition-colors opacity-0">
              <td className="p-4 text-skyblue">{cred.id}</td>
              <td className="p-4">
                <span className={`px-2 py-1 rounded text-[10px] border ${
                  cred.type === 'Admin' ? 'border-lavender text-lavender' : 'border-grey text-grey'
                }`}>
                  {cred.type}
                </span>
              </td>
              <td className="p-4 text-white">{cred.email}</td>
              <td className="p-4 text-grey">{cred.domain}</td>
              <td className="p-4">
                <span className="text-red font-bold animate-pulse">
                  {cred.exposure}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CredentialTable;