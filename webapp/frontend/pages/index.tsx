import React, { useState, useEffect } from 'react';
import { IndicatorList, Indicator } from '../components/IndicatorList';
import { formatCronjobDate } from '../utils/formatCronjobDate';

export default function Home() {
  const [analysedCoins, setAnalysedCoins] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedToken, setSelectedToken] = useState('BTC');

  const [showCronjobs, setShowCronjobs] = useState(false);
  const [cronjobs, setCronjobs] = useState<any[]>([]);
  const [cronLoading, setCronLoading] = useState(false);

  const [loading, setLoading] = useState(false);
  // Correct order and labels for technical and social indicators
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

  const [technicalIndicators, setTechnicalIndicators] = useState<Indicator[]>([
    { name: 'Trading Volume', value: 0, max: 0 },
    { name: 'Liquidity', value: 0, max: 0 },
    { name: 'Whale Transactions', value: 0, max: 0 },
    { name: 'Token Distribution', value: 0, max: 0 },
    { name: 'Pre-Sale Vesting', value: 0, max: 0 },
    { name: 'Smart Contract Audit', value: 0, max: 0 },
  ]);
  const [socialIndicators, setSocialIndicators] = useState<Indicator[]>([
    { name: 'Social Volume', value: 0, max: 0 },
    { name: 'Sentiment Analysis', value: 0, max: 0 },
    { name: 'Developer Activity', value: 0, max: 0 },
  ]);
  const [totalScore, setTotalScore] = useState(0);
  const [recommendation, setRecommendation] = useState('');
  const [recommendationDesc, setRecommendationDesc] = useState('');

  // Map recommendation to color classes
  const recommendationColor = {
    'STRONG BUY': 'text-[#2DE282]', // bright green
    'BUY': 'text-[#00FFB2]',       // teal
    'HOLD': 'text-[#FFD600]',      // yellow
    'WATCH': 'text-[#FF6A00]',     // orange
    'AVOID': 'text-[#FF3B3B]',     // red
    '': 'text-[#888888]'           // gray for no label
  };


  useEffect(() => {
    // Fetch only analysed coins for dropdown
    fetch('/api/analysed_coins')
      .then(res => res.json())
      .then(data => {
        setAnalysedCoins(data);
        // If BTC exists, default to BTC, else first coin
        if (data && data.length > 0) {
          setSelectedToken(data.includes('BTC') ? 'BTC' : data[0]);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/indicators?token=${selectedToken}`)
      .then(res => res.json())
      .then(data => {
        // Filter and order technical indicators
        let technical = (data.technical || []).filter((i: Indicator) => TECHNICAL_LABELS.includes(i.name));
        technical = TECHNICAL_LABELS.map(label => technical.find((i: Indicator) => i.name === label) || { name: label, value: 0, max: 0 });
        setTechnicalIndicators(technical);
        // Filter and order social indicators
        let social = (data.social || []).filter((i: Indicator) => SOCIAL_LABELS.includes(i.name));
        social = SOCIAL_LABELS.map(label => social.find((i: Indicator) => i.name === label) || { name: label, value: 0, max: 0 });
        setSocialIndicators(social);
        // Use backend-computed score_percentage if available, else fall back to local calculation
        const techScore = technical.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
        const techMax = technical.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
        const socScore = social.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
        const socMax = social.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
        const total = techScore + socScore;
        const totalMax = techMax + socMax;
        const percent = typeof data.score_percentage === 'number' ? data.score_percentage : (totalMax > 0 ? (100 * total / totalMax) : 0);
        setTotalScore(percent);
        // Recommendation logic from .env and backend
        let rec = '', desc = '';
        if (percent >= 50) { rec = 'BUY'; desc = 'Good potential for growth'; }
        else if (percent >= 40) { rec = 'HOLD'; desc = 'Moderate potential'; }
        else if (percent >= 30) { rec = 'WATCH'; desc = 'Some concerns'; }
        else if (percent >= 20) { rec = 'AVOID'; desc = 'Significant concerns'; }
        else { rec = ''; desc = ''; }
        setRecommendation(rec);
        setRecommendationDesc(desc);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [selectedToken]);

  // Fetch cronjobs when modal is opened
  useEffect(() => {
    if (showCronjobs) {
      setCronLoading(true);
      fetch('/api/cronjobs')
        .then(res => res.json())
        .then(data => setCronjobs(data))
        .catch(() => setCronjobs([]))
        .finally(() => setCronLoading(false));
    }
  }, [showCronjobs]);

  return (
    <>
      <div className="min-h-screen flex items-center justify-center bg-[#121212] font-inter px-2 sm:px-4">
        <div className="bg-[#1A1A1A] text-[#FF6A00] rounded-2xl p-4 sm:p-6 md:p-8 lg:p-12 w-full max-w-[98vw] sm:max-w-[400px] md:max-w-[520px] lg:max-w-[700px] mx-auto shadow-lg">
          {/* Header */}
          {/* Responsive header layout: horizontal on desktop, stacked/centered on mobile */}
          <div className="flex flex-row items-center justify-between w-full mb-4 lg:mb-8 gap-4">
            {/* Left: Coin dropdown */}
            <div className="flex flex-col items-start w-[220px] gap-2">
              <div className="relative w-full max-w-[220px]">
                <button
                  className="w-full bg-[#242424] text-[#FF6A00] text-base sm:text-lg lg:text-xl rounded-lg px-4 py-2 flex items-center justify-between focus:outline-none border-2 border-transparent focus:border-transparent hover:border-transparent active:border-transparent transition-colors"
                  onClick={() => setShowDropdown(d => !d)}
                  type="button"
                  style={{ minHeight: '44px' }}
                >
                  {selectedToken}
                  <svg className="ml-2 w-4 h-4 text-[#FF6A00]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
                </button>
                {showDropdown && (
                  <div className="absolute z-10 w-full coin-dropdown-menu rounded-lg shadow-lg mt-2 max-h-60 overflow-auto border border-[#333]">
                    {analysedCoins.map(symbol => (
                      <div
                        key={symbol}
                        className={`px-4 py-2 cursor-pointer ${symbol === selectedToken ? 'bg-[#333] text-[#FF6A00]' : 'text-[#FF6A00] hover:bg-[#222] active:bg-[#222]'}`}
                        style={{ minHeight: '40px' }}
                        onClick={() => { setSelectedToken(symbol); setShowDropdown(false); }}
                      >
                        {symbol}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            {/* MEXC Spot link under dropdown */}
            <div className="w-full flex justify-center">
              <a
                href={`https://www.mexc.com/de-DE/exchange/${selectedToken}_USDT`}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 text-[#2DE282] underline text-sm hover:text-[#FF6A00] transition-colors text-center"
                style={{ display: 'inline-block' }}
              >
                View on MEXC
              </a>
            </div>
          </div>
          {/* Center: Big percent and claim stacked */}
            <div className="flex flex-col items-center justify-center flex-1 gap-2 mx-2 text-center">
              <span className={`text-2xl sm:text-3xl lg:text-5xl text-center mx-auto ${recommendationColor[recommendation] || 'text-[#2DE282]'}`}
                style={{ textShadow: '0 0 2px #000, 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000' }}
              >
                {Math.floor(totalScore)}%
              </span>
            </div>
            {/* Right: Cronjobs button */}
            <div className="flex flex-row items-center gap-3 justify-end w-full sm:w-auto">
              <button
                className="w-full sm:w-auto bg-[#242424] text-[#FF6A00] text-xs sm:text-sm lg:text-lg px-3 py-1.5 sm:px-4 sm:py-2 lg:px-6 lg:py-3 rounded-lg hover:text-[#FFA64D] cursor-pointer border-none outline-none transition-colors mt-3 sm:mt-0 max-w-[220px]"
                onClick={() => setShowCronjobs(true)}
              >
                Cronjobs
              </button>
            </div>
          </div>

          {/* Indicators Row: Technical (left) and Social (right) on desktop */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
            {/* Technical Indicators */}
            <div>
              <div className="flex justify-between items-center mb-2 mt-4">
                <span className="uppercase text-[#FF6A00] text-base sm:text-lg lg:text-xl px-2 sm:px-3">Technical</span>
                <span className="text-[#2DE282] text-base sm:text-base lg:text-lg text-right px-2 sm:px-3">{(() => {
                  const score = technicalIndicators.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
                  const max = technicalIndicators.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
                  return `${score.toFixed(1)}/${max}`;
                })()}</span>
              </div>
              <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-2">
                <IndicatorList indicators={technicalIndicators} loading={loading} />
              </div>
            </div>
            {/* Social */}
            <div>
              <div className="flex justify-between items-center mb-2 mt-4">
                <span className="uppercase text-[#FF6A00] text-base sm:text-lg lg:text-xl px-2 sm:px-3">Social</span>
                <span className="text-[#2DE282] text-base sm:text-base lg:text-lg text-right px-2 sm:px-3">{(() => {
                  const score = socialIndicators.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
                  const max = socialIndicators.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
                  return max > 0 ? `${score}/${max}` : '0';
                })()}</span>
              </div>
              <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-2">
                <IndicatorList indicators={socialIndicators} loading={loading} />
              </div>
            </div>
          </div>
        </div>
        {/* Modal Overlay */}
        {showCronjobs && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
            <div className="bg-[#232323] rounded-2xl shadow-xl p-6 w-full max-w-2xl relative animate-fade-in">
              <button
                className="absolute top-3 right-4 text-[#FF6A00] text-2xl hover:text-[#FFA64D] focus:outline-none"
                onClick={() => setShowCronjobs(false)}
                aria-label="Close"
              >
                ×
              </button>
              <h2 className="text-[#FF6A00] text-xl mb-4">Cronjobs</h2>
              <div className="text-[#FFDEB4] text-sm">
                {cronLoading ? (
                  <div className="py-4 text-center">Loading...</div>
                ) : cronjobs.length === 0 ? (
                  <div className="py-4 text-center">No cronjobs found.</div>
                ) : (
                  <ul className="space-y-2">
                    {[...cronjobs]
                      .map(job => {
                        // Attach a sortable date property
                        try {
                          const parts = job.schedule.split(' ');
                          if (parts.length < 5) throw new Error('Invalid cron format');
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
                      })
                      .sort((a, b) => {
                        if (a._sortDate && b._sortDate) return a._sortDate - b._sortDate;
                        if (a._sortDate) return -1;
                        if (b._sortDate) return 1;
                        return 0;
                      })
                      .map(job => (
                      <li key={job.id} className="flex justify-between items-center bg-[#292929] rounded-lg px-4 py-2">
                        <span className="text-[#2DE282] font-semibold w-1/3 text-base sm:text-lg">
                          {formatCronjobDate(job.schedule)}
                        </span>
                        <span className="text-white break-all w-2/3 text-center text-base sm:text-lg">{job.command.replace('/usr/bin/python -m', '').replace('Trade.main', '').trim()}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

