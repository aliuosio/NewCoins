import { useState, useEffect } from 'react';

interface CoinData {
  id: number;
  name: string;
  symbol: string;
  time_start: string | null;
  time_buy: string | null;
  time_sell: string | null;
  price_buy: number | null;
  price_sell: number | null;
  fund_buy: number | null;
  fund_sell: number | null;
  profit: number | null;
  futures?: boolean;
  [key: string]: any;
}

/**
 * Custom hook to fetch coin data for a specific symbol
 * @param symbol The coin symbol to fetch data for
 * @returns Object containing coin data and loading state
 */
export const useCoinData = (symbol: string): { 
  data: CoinData | null; 
  loading: boolean;
  error: string | null;
} => {
  const [data, setData] = useState<CoinData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) {
      setData(null);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    fetch(`/api/coin/${symbol}`)
      .then(res => {
        if (!res.ok) {
          if (res.status === 404) {
            throw new Error(`Symbol '${symbol}' not found`);
          }
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        setData(data);
      })
      .catch(err => {
        setError(err.message || 'Failed to fetch coin data');
        setData(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [symbol]);

  return { data, loading, error };
};
