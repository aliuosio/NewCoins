import { useState, useEffect } from 'react';

interface Cronjob {
  id: number;
  schedule: string;
  command: string;
  _sortDate?: Date | null;
}

/**
 * Custom hook to fetch and process cronjobs
 * @param shouldFetch Boolean flag to determine if cronjobs should be fetched
 * @returns Object containing cronjobs array and loading state
 */
export const useCronjobs = (shouldFetch: boolean): { 
  cronjobs: Cronjob[]; 
  loading: boolean;
  error: string | null;
} => {
  const [cronjobs, setCronjobs] = useState<Cronjob[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!shouldFetch) return;
    
    setLoading(true);
    setError(null);

    fetch('/api/cronjobs')
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        // Process and sort cronjobs
        const processedJobs = data.map((job: Cronjob) => {
          // Attach a sortable date property
          try {
            const parts = job.schedule.split(' ');
            if (parts.length < 5) return { ...job, _sortDate: null };
            
            const [min, hour, day, month] = parts;
            const date = new Date(Date.UTC(
              new Date().getFullYear(),
              parseInt(month) - 1,
              parseInt(day),
              parseInt(hour),
              parseInt(min)
            ));
            return { ...job, _sortDate: date };
          } catch {
            return { ...job, _sortDate: null };
          }
        }).sort((a: Cronjob, b: Cronjob) => {
          if (a._sortDate && b._sortDate) return a._sortDate.getTime() - b._sortDate.getTime();
          if (a._sortDate) return -1;
          if (b._sortDate) return 1;
          return 0;
        });
        
        setCronjobs(processedJobs);
      })
      .catch(err => {
        setError(err.message || 'Failed to fetch cronjobs');
        setCronjobs([]);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [shouldFetch]);

  return { cronjobs, loading, error };
};
