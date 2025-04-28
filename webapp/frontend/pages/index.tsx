import React, { useState, useEffect } from 'react';
import { Indicator } from '../components/IndicatorList';
import CoinDropdown from '../components/CoinDropdown';
import TimeDisplay from '../components/TimeDisplay';
import ScoreDisplay from '../components/ScoreDisplay';
import CronjobsModal from '../components/CronjobsModal';
import IndicatorSection from '../components/IndicatorSection';
import { useAnalysedCoins } from '../hooks/useAnalysedCoins';
import { useCoinData } from '../hooks/useCoinData';
import { useIndicators } from '../hooks/useIndicators';
import { useCronjobs } from '../hooks/useCronjobs';

/**
 * Main home page component
 */
export default function Home() {
  // Define constants for indicator labels
  const TECHNICAL_LABELS = [
    'Trading Volume',
    'Liquidity',
    'Whale Transactions',
    'Token Distribution',
    'Pre-Sale Vesting',
    'Smart Contract Audit',
  ];
  
  const SOCIAL_LABELS = [
    'Social Volume',
    'Sentiment Analysis',
    'Developer Activity',
  ];

  // State for UI controls
  const [showDropdown, setShowDropdown] = useState(false);
  const [showCronjobsModal, setShowCronjobsModal] = useState(false);
  
  // Token selection state
  const [selectedToken, setSelectedToken] = useState<string>('GOLD'); // Default to GOLD
  
  // Helper function to get recommendation based on score
  const getRecommendation = (score: number) => {
    if (score >= 50) return { recommendation: 'BUY', description: 'Good potential for growth' };
    else if (score >= 40) return { recommendation: 'HOLD', description: 'Moderate potential' };
    else if (score >= 30) return { recommendation: 'WATCH', description: 'Some concerns' };
    else if (score >= 20) return { recommendation: 'AVOID', description: 'Significant concerns' };
    else return { recommendation: '', description: '' };
  };
  
  // Data states
  const [coinData, setCoinData] = useState<any>(null);
  const [indicatorsData, setIndicatorsData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  
  // Get available coins
  const { coins: analysedCoins } = useAnalysedCoins();
  
  // Cronjobs data
  const { cronjobs, loading: cronjobsLoading } = useCronjobs(showCronjobsModal);
  
  // Handle token selection
  const handleTokenSelect = (token: string) => {
    if (token !== selectedToken) {
      setSelectedToken(token);
    }
  };
  
  // Fetch data when token changes
  useEffect(() => {
    if (!selectedToken) return;
    
    let isMounted = true;
    setLoading(true);
    
    // Fetch coin data
    fetch(`/api/coin/${selectedToken}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (isMounted) setCoinData(data);
      })
      .catch(() => {
        if (isMounted) setCoinData(null);
      });
    
    // Fetch indicators data
    fetch(`/api/indicators?token=${selectedToken}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (isMounted) {
          setIndicatorsData(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setIndicatorsData(null);
          setLoading(false);
        }
      });
    
    return () => { isMounted = false; };
  }, [selectedToken]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#121212] font-inter px-2 sm:px-4">
      <div className="bg-[#1A1A1A] text-[#FF6A00] rounded-2xl p-4 sm:p-6 md:p-8 lg:p-12 w-full max-w-[98vw] sm:max-w-[400px] md:max-w-[520px] lg:max-w-[700px] mx-auto shadow-lg">
        {/* Header */}
        <div className="flex flex-row items-start justify-between w-full mb-4 lg:mb-8 gap-4">
          {/* Left: Coin dropdown with time display */}
          <div className="flex flex-col items-start">
            <CoinDropdown
              selectedToken={selectedToken}
              analysedCoins={analysedCoins}
              onSelect={handleTokenSelect}
              onToggleDropdown={() => setShowDropdown(!showDropdown)}
              showDropdown={showDropdown}
              loading={loading}
            />
            
            {/* Display time_start if available */}
            {coinData && coinData.time_start && (
              <TimeDisplay 
                timestamp={coinData.time_start}
                className="mt-2"
              />
            )}
          </div>
          
          {/* Center: Score display */}
          {indicatorsData && (
            <ScoreDisplay 
              score={indicatorsData.score_percentage || 0}
              recommendation={getRecommendation(indicatorsData.score_percentage || 0).recommendation}
              recommendationDesc={getRecommendation(indicatorsData.score_percentage || 0).description}
              selectedToken={selectedToken}
            />
          )}
          
          {/* Right: Cronjobs button */}
          <div className="flex flex-row items-center gap-3 justify-end w-full sm:w-auto">
            <button
              className="w-full max-w-[220px] bg-[#242424] text-[#FF6A00] rounded-lg px-4 py-2 flex items-center justify-center focus:outline-none border-2 border-transparent focus:border-transparent hover:border-transparent active:border-transparent transition-colors mt-3 sm:mt-0 uppercase"
              style={{ minHeight: '44px' }}
              onClick={() => setShowCronjobsModal(true)}
            >
              Cronjobs
            </button>
          </div>
        </div>

        {/* Indicators Row: Technical (left) and Social (right) on desktop */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          {/* Technical Indicators */}
          {indicatorsData && (
            <IndicatorSection 
              title="Technical"
              indicators={indicatorsData.technical}
              loading={loading}
            />
          )}
          
          {/* Social Indicators */}
          {indicatorsData && (
            <IndicatorSection 
              title="Social"
              indicators={indicatorsData.social}
              loading={loading}
            />
          )}
        </div>
      </div>
      
      {/* Cronjobs Modal */}
      <CronjobsModal 
        isOpen={showCronjobsModal}
        onClose={() => setShowCronjobsModal(false)}
        cronjobs={cronjobs}
        loading={cronjobsLoading}
      />
    </div>
  );
}
