import React, { useState } from 'react';
import { Search, Filter, Terminal, Loader } from 'lucide-react';
import SearchFilters from '../components/search/SearchFilters';
import SearchResults from '../components/search/SearchResults';

const SearchPage = () => {
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchKey, setSearchKey] = useState(0); // Force re-render of SearchResults

  const handleSearch = () => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    // Trigger SearchResults refresh by changing key
    setSearchKey(prev => prev + 1);
    
    // Reset after animation
    setTimeout(() => {
      setIsSearching(false);
    }, 500);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-7xl mx-auto">
      
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Intelligence <span className="text-skyblue">Search</span>
        </h1>
        <p className="text-grey font-mono text-sm">
          Query the centralized breach database...
        </p>
      </div>

      {/* SEARCH COMMAND BAR */}
      <div className="glass-panel p-2 rounded-xl border border-white/10 flex items-center gap-4 relative z-20 shadow-2xl">
        <div className="pl-4 text-grey">
          <Terminal size={20} />
        </div>
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Search by keyword, email domain, IP, or credential hash..."
          className="bg-transparent border-none outline-none text-white w-full font-mono text-lg placeholder:text-white/20 h-12"
        />
        <div className="pr-2 flex gap-2">
          <button 
            onClick={() => setIsFiltersOpen(!isFiltersOpen)}
            className={`p-3 rounded-lg border transition-all duration-300 flex items-center gap-2 text-sm font-mono ${
              isFiltersOpen 
                ? 'bg-skyblue/10 border-skyblue text-skyblue' 
                : 'border-white/10 text-grey hover:text-white hover:bg-white/5'
            }`}
          >
            <Filter size={16} />
            <span className="hidden md:inline">FILTERS</span>
          </button>
          
          <button 
            onClick={handleSearch}
            disabled={isSearching || !query.trim()}
            className="bg-white text-background px-6 py-3 rounded-lg font-bold hover:bg-grey transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSearching ? (
              <Loader className="animate-spin" size={18} />
            ) : (
              <Search size={18} />
            )}
            <span className="hidden md:inline">SEARCH</span>
          </button>
        </div>
      </div>

      {/* FILTER PANEL (Collapsible) */}
      <SearchFilters isOpen={isFiltersOpen} onClose={() => setIsFiltersOpen(false)} />

      {/* RESULTS AREA */}
      <SearchResults key={searchKey} searchQuery={query} />

    </div>
  );
};

export default SearchPage;