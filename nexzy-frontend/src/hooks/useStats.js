import { useEffect, useState } from 'react';
import { fetchStats } from '../lib/api';

export function useStats(token) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      try {
        const data = await fetchStats(token);
        if (mounted) setStats(data);
      } catch (e) {
        if (mounted) setError(e);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    if (token) {
      load();
    } else {
      // still try without token if public route
      load();
    }
    return () => { mounted = false; };
  }, [token]);

  return { stats, loading, error };
}
