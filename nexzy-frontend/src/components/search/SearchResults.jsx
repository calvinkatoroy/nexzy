import React, { useState, useEffect } from 'react';
import { animate, stagger } from 'animejs';
import { ExternalLink, Eye, Loader } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';

const SearchResults = ({ searchQuery }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (searchQuery && searchQuery.trim()) {
      loadResults();
    } else {
      // Show all results if no query
      loadAllResults();
    }
  }, [searchQuery]);

  const loadResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const searchResults = await api.search({ q: searchQuery });
      setResults(searchResults);
      setLoading(false);
      
      // Animate after data loads only if we have results
      if (searchResults.length > 0) {
        setTimeout(() => {
          animate('.result-row', {
            opacity: [0, 1],
            x: [-10, 0],
            delay: stagger(60, { start: 200 }),
            ease: 'outQuad'
          });
        }, 100);
      }
    } catch (err) {
      console.error('Failed to load results:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const loadAllResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const allResults = await api.search({});
      setResults(allResults);
      setLoading(false);
      
      if (allResults.length > 0) {
        setTimeout(() => {
          animate('.result-row', {
            opacity: [0, 1],
            x: [-10, 0],
            delay: stagger(60, { start: 200 }),
            ease: 'outQuad'
          });
        }, 100);
      }
    } catch (err) {
      console.error('Failed to load all results:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const getSeverityFromScore = (score) => {
    if (score >= 0.7) return 'Critical';
    if (score >= 0.5) return 'High';
    if (score >= 0.3) return 'Medium';
    return 'Low';
  };

  const getSeverityColor = (sev) => {
    switch(sev) {
      case 'Critical': return 'text-red border-red/30 bg-red/10';
      case 'High': return 'text-orange border-orange/30 bg-orange/10';
      case 'Medium': return 'text-yellow border-yellow/30 bg-yellow/10';
      default: return 'text-grey border-grey/30 bg-grey/10';
    }
  };

  const getTypeFromData = (result) => {
    if (result.has_credentials) return 'Credentials';
    if (result.target_emails?.length > 0) return 'Email';
    return 'Data';
  };

  const getTypeColor = (type) => {
    if (type.includes('Email')) return 'text-lavender';
    if (type.includes('Credentials')) return 'text-red';
    return 'text-white';
  };

  const exportToCSV = () => {
    if (results.length === 0) return;

    // CSV headers
    const headers = ['URL', 'Source', 'Author', 'Type', 'Score', 'Emails', 'Target Emails', 'Found At'];
    
    // CSV rows
    const rows = results.map(res => {
      const type = getTypeFromData(res);
      return [
        res.url,
        res.source,
        res.author || 'N/A',
        type,
        (res.relevance_score * 100).toFixed(0) + '%',
        res.emails?.length || 0,
        res.target_emails?.length || 0,
        new Date(res.found_at).toLocaleString()
      ];
    });

    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `nexzy_search_results_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="glass-panel rounded-xl border border-white/10 p-12 flex items-center justify-center">
        <Loader className="animate-spin text-skyblue" size={32} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel rounded-xl border border-white/10 p-8 text-center">
        <p className="text-red">Failed to load results: {error}</p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-xl overflow-hidden border border-white/10">
      {/* Header */}
      <div className="bg-white/5 px-6 py-3 border-b border-white/10 flex justify-between items-center">
        <span className="text-xs text-grey font-mono">FOUND {results.length} RESULTS</span>
        <button 
          onClick={exportToCSV}
          disabled={results.length === 0}
          className="text-xs text-skyblue hover:text-white transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ExternalLink size={12} /> EXPORT CSV
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="text-xs text-grey uppercase tracking-wider border-b border-white/10">
              <th className="px-6 py-4 font-normal">URL</th>
              <th className="px-6 py-4 font-normal">Source</th>
              <th className="px-6 py-4 font-normal">Type</th>
              <th className="px-6 py-4 font-normal">Score</th>
              <th className="px-6 py-4 font-normal">Target Emails</th>
              <th className="px-6 py-4 font-normal text-right">Action</th>
            </tr>
          </thead>
          <tbody className="font-mono text-sm">
            {results.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-grey">
                  No results yet. Create a scan to start discovering breaches.
                </td>
              </tr>
            ) : (
              results.map((res, i) => {
                const severity = getSeverityFromScore(res.relevance_score);
                const type = getTypeFromData(res);
                
                return (
                  <tr key={i} className="result-row opacity-0 border-b border-white/5 hover:bg-white/5 transition-colors group">
                    <td className="px-6 py-4">
                      <a 
                        href={res.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-skyblue hover:text-white flex items-center gap-1 max-w-[200px] truncate"
                      >
                        {res.url.split('/').pop()}
                        <ExternalLink size={12} />
                      </a>
                    </td>
                    <td className="px-6 py-4 text-grey">{res.source}</td>
                    <td className={`px-6 py-4 ${getTypeColor(type)}`}>{type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-[10px] border font-bold uppercase ${getSeverityColor(severity)}`}>
                        {(res.relevance_score * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-white">
                      {res.target_emails?.length || 0}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {res.alert_id ? (
                        <Link to={`/alerts/${res.alert_id}`} className="inline-block p-2 hover:bg-white/10 rounded text-grey hover:text-white transition-colors">
                          <Eye size={16} />
                        </Link>
                      ) : (
                        <span className="inline-block p-2 text-grey/30 cursor-not-allowed" title="No alert available">
                          <Eye size={16} />
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SearchResults;