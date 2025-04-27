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
  const [selectedToken, setSelectedToken] = useState('');

  // Custom hooks for data fetching
  const { coins: analysedCoins, initialCoin, loading: coinsLoading } = useAnalysedCoins();
  
  // Set initial token if not already set and we have an initialCoin
  useEffect(() => {
    if (!selectedToken && initialCoin) {
      setSelectedToken(initialCoin);
    }
  }, [initialCoin, selectedToken]);
  
  // Only fetch data when we have a valid token
  const activeToken = selectedToken || initialCoin;
  const { data: coinData } = useCoinData(activeToken || '');
  
  const { data: indicatorsData, loading: indicatorsLoading } = useIndicators(
    activeToken || '',
    TECHNICAL_LABELS,
    SOCIAL_LABELS
  );
  
  const { cronjobs, loading: cronjobsLoading } = useCronjobs(showCronjobsModal);

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
              onSelect={setSelectedToken}
              onToggleDropdown={() => setShowDropdown(!showDropdown)}
              showDropdown={showDropdown}
              loading={indicatorsLoading}
            />
            
            {/* Display time_start if available */}
            {coinData && coinData.time_start && (
              <TimeDisplay 
                label="Time Start"
                timestamp={coinData.time_start}
                className="mt-2"
              />
            )}
          </div>
          
          {/* Center: Score display */}
          {indicatorsData && (
            <ScoreDisplay 
              score={indicatorsData.totalScore}
              recommendation={indicatorsData.recommendation}
              recommendationDesc={indicatorsData.recommendationDesc}
              selectedToken={selectedToken || initialCoin}
            />
          )}
          
          {/* Right: Cronjobs button */}
          <div className="flex flex-row items-center gap-3 justify-end w-full sm:w-auto">
            <button
              className="w-full max-w-[220px] bg-[#242424] text-[#FF6A00] text-base sm:text-lg lg:text-xl rounded-lg px-4 py-2 flex items-center justify-center focus:outline-none border-2 border-transparent focus:border-transparent hover:border-transparent active:border-transparent transition-colors mt-3 sm:mt-0"
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
              loading={indicatorsLoading}
            />
          )}
          
          {/* Social Indicators */}
          {indicatorsData && (
            <IndicatorSection 
              title="Social"
              indicators={indicatorsData.social}
              loading={indicatorsLoading}
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
