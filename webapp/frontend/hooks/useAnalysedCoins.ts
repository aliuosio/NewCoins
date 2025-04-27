import { useState, useEffect } from 'react';

/**
 * Custom hook to fetch available analysed coins
 * @returns Object containing coins array and loading state
 */
export const useAnalysedCoins = (): { 
  coins: string[]; 
  loading: boolean;
  error: string | null;
  initialCoin: string;
} => {
  const [coins, setCoins] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [initialCoin, setInitialCoin] = useState<string>('');

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch('/api/analysed_coins')
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        setCoins(data);
        
        // Set initial coin (BTC if available, otherwise first coin)
        if (data && data.length > 0) {
          const defaultCoin = data.includes('BTC') ? 'BTC' : data[0];
          setInitialCoin(defaultCoin);
        } else {
          // Fallback to GOLD if no coins are returned
          setInitialCoin('GOLD');
        }
      })
      .catch(err => {
        setError(err.message || 'Failed to fetch analysed coins');
        setCoins([]);
        // Fallback to GOLD if there's an error
        setInitialCoin('GOLD');
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return { coins, loading, error, initialCoin };
};
