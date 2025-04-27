import { useState, useEffect } from 'react';
import { Indicator } from '../components/IndicatorList';

interface IndicatorsData {
  technical: Indicator[];
  social: Indicator[];
  totalScore: number;
  recommendation: string;
  recommendationDesc: string;
}

/**
 * Custom hook to fetch and process indicators data
 * @param symbol The coin symbol to fetch indicators for
 * @param technicalLabels Array of expected technical indicator labels
 * @param socialLabels Array of expected social indicator labels
 * @returns Object containing processed indicators data and loading state
 */
export const useIndicators = (
  symbol: string,
  technicalLabels: string[],
  socialLabels: string[]
): { 
  data: IndicatorsData; 
  loading: boolean;
  error: string | null;
} => {
  const [data, setData] = useState<IndicatorsData>({
    technical: technicalLabels.map(name => ({ name, value: 0, max: 0 })),
    social: socialLabels.map(name => ({ name, value: 0, max: 0 })),
    totalScore: 0,
    recommendation: '',
    recommendationDesc: ''
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;

    setLoading(true);
    setError(null);

    fetch(`/api/indicators?token=${symbol}`)
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then(responseData => {
        // Process technical indicators
        let technical = (responseData.technical || [])
          .filter((i: Indicator) => technicalLabels.includes(i.name));
        
        technical = technicalLabels.map(label => 
          technical.find((i: Indicator) => i.name === label) || 
          { name: label, value: 0, max: 0 }
        );

        // Process social indicators
        let social = (responseData.social || [])
          .filter((i: Indicator) => socialLabels.includes(i.name));
        
        social = socialLabels.map(label => 
          social.find((i: Indicator) => i.name === label) || 
          { name: label, value: 0, max: 0 }
        );

        // Calculate scores
        const techScore = technical.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
        const techMax = technical.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
        const socScore = social.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
        const socMax = social.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
        
        const total = techScore + socScore;
        const totalMax = techMax + socMax;
        const percent = typeof responseData.score_percentage === 'number' 
          ? responseData.score_percentage 
          : (totalMax > 0 ? (100 * total / totalMax) : 0);

        // Determine recommendation
        let rec = '', desc = '';
        if (percent >= 50) { rec = 'BUY'; desc = 'Good potential for growth'; }
        else if (percent >= 40) { rec = 'HOLD'; desc = 'Moderate potential'; }
        else if (percent >= 30) { rec = 'WATCH'; desc = 'Some concerns'; }
        else if (percent >= 20) { rec = 'AVOID'; desc = 'Significant concerns'; }
        else { rec = ''; desc = ''; }

        setData({
          technical,
          social,
          totalScore: percent,
          recommendation: rec,
          recommendationDesc: desc
        });
      })
      .catch(err => {
        setError(err.message || 'Failed to fetch indicators');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [symbol, technicalLabels, socialLabels]);

  return { data, loading, error };
};
