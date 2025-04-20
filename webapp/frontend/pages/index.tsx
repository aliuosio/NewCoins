import React, { useState, useEffect } from 'react';
import parser from 'cron-parser';
import { DateTime } from 'luxon';

export default function Home() {
  const [analysedCoins, setAnalysedCoins] = useState<string[]>([]);
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

  const [technicalIndicators, setTechnicalIndicators] = useState([
    { name: 'Trading Volume', value: 0 },
    { name: 'Liquidity', value: 0 },
    { name: 'Whale Transactions', value: 0 },
    { name: 'Token Distribution', value: 0 },
    { name: 'Pre-Sale Vesting', value: 0 },
    { name: 'Smart Contract Audit', value: 0 },
  ]);
  const [socialIndicators, setSocialIndicators] = useState([
    { name: 'Social Volume', value: 0 },
    { name: 'Sentiment Analysis', value: 0 },
    { name: 'Developer Activity', value: 0 },
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
        let technical = (data.technical || []).filter(i => TECHNICAL_LABELS.includes(i.name));
        technical = TECHNICAL_LABELS.map(label => technical.find(i => i.name === label) || { name: label, value: 0 });
        setTechnicalIndicators(technical);
        // Filter and order social indicators
        let social = (data.social || []).filter(i => SOCIAL_LABELS.includes(i.name));
        social = SOCIAL_LABELS.map(label => social.find(i => i.name === label) || { name: label, value: 0 });
        setSocialIndicators(social);
        // Compute total score as percent
        const techScore = technical.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
        const techMax = technical.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
        const socScore = social.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
        const socMax = social.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
        const total = techScore + socScore;
        const totalMax = techMax + socMax;
        const percent = totalMax > 0 ? (100 * total / totalMax) : 0;
        setTotalScore(percent);
        // Recommendation logic from README
        let rec = '', desc = '';
        if (percent >= 80) { rec = 'STRONG BUY'; desc = 'High potential for growth'; }
        else if (percent >= 70) { rec = 'BUY'; desc = 'Good potential for growth'; }
        else if (percent >= 60) { rec = 'HOLD'; desc = 'Moderate potential'; }
        else if (percent >= 50) { rec = 'WATCH'; desc = 'Some concerns'; }
        else { rec = 'AVOID'; desc = ''; }
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
        <div className="bg-[#1A1A1A] text-[#FF6A00] rounded-2xl p-4 sm:p-6 md:p-8 lg:p-12 w-full max-w-[98vw] sm:max-w-[400px] md:max-w-[520px] lg:max-w-[700px] shadow-lg">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-10 lg:mb-14 gap-4">
            {/* Left: Token selector */}
            <div className="flex flex-row items-center gap-3">
              <select
                className="bg-[#242424] text-[#FF6A00] px-3 py-1.5 sm:px-4 sm:py-2 lg:px-6 lg:py-3 rounded-lg font-bold text-sm sm:text-base lg:text-xl appearance-none focus:outline-none focus:ring-2 focus:ring-[#FF6A00] cursor-pointer"
                value={selectedToken}
                onChange={e => setSelectedToken(e.target.value)}
              >
                {analysedCoins.map(symbol => (
                  <option key={symbol} value={symbol}>
                    {symbol}
                  </option>
                ))}
              </select>
            </div>
            {/* Center: Percent and risk level stacked */}
            <div className="flex flex-col items-center justify-center flex-1">
              <span className={`text-2xl sm:text-3xl lg:text-5xl font-bold text-center ${recommendationColor[recommendation] || 'text-[#2DE282]'}`}
                style={{ textShadow: '0 0 2px #000, 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000' }}
              >
                {Math.round(totalScore)}%
              </span>
              {recommendation && recommendation === 'AVOID' && (
                <span className="font-bold text-base sm:text-lg lg:text-xl text-[#FF3B3B] mt-1" style={{ letterSpacing: '0.04em' }}>
                  {recommendation}
                </span>
              )}
              {recommendation && recommendation !== 'AVOID' && (
                <span className={`font-bold text-base sm:text-lg lg:text-xl mt-1 ${recommendationColor[recommendation] || 'text-[#888888]'}`}
                  style={{ letterSpacing: '0.04em' }}
                >
                  {recommendation}
                </span>
              )}
            </div>
            {/* Right: Cronjobs button */}
            <div className="flex flex-row items-center gap-3 justify-end">
              <button
                className="bg-[#242424] text-[#FF6A00] font-bold text-xs sm:text-sm lg:text-lg px-3 py-1.5 sm:px-4 sm:py-2 lg:px-6 lg:py-3 rounded-lg hover:text-[#FFA64D] cursor-pointer border-none outline-none transition-colors"
                onClick={() => setShowCronjobs(true)}
              >
                Cronjobs
              </button>
            </div>
          </div>

          {/* Indicators Row: Social (left on desktop), Technical (right) */}
          <div className="flex flex-col gap-8">
            {/* Technical Indicators */}
            <div className="flex-1">
              <div className="flex justify-between items-center mb-2 mt-6">
                <span className="uppercase font-bold text-[#FF6A00] text-base sm:text-lg lg:text-xl px-2 sm:px-3">Technical Indicators</span>
                <span className="font-bold text-[#2DE282] text-base sm:text-base lg:text-lg text-right px-2 sm:px-3">Score: {(() => {
                  const score = technicalIndicators.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
                  const max = technicalIndicators.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
                  return max > 0 ? `${score}/${max} pts` : '0 pts';
                })()}</span>
              </div>
              <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-6">
                <div className="space-y-3">
                  {loading ? (
                    <div className="text-center text-[#FF6A00] py-4">Loading...</div>
                  ) : (
                    <>
                      {technicalIndicators.map((indicator, idx) => (
                        <div key={indicator.name} className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                          <span className="flex items-center gap-2">
                            {indicator.name === 'Trading Volume' && <span>📊</span>}
                            {indicator.name === 'Liquidity' && <span>💧</span>}
                            {indicator.name === 'Whale Transactions' && <span>🐳</span>}
                            {indicator.name === 'Token Distribution' && <span>📈</span>}
                            {indicator.name === 'Pre-Sale Vesting' && <span>📆</span>}
                            {indicator.name === 'Smart Contract Audit' && <span>📝</span>}
                            <span className="text-[#FF6A00] font-bold text-base sm:text-lg lg:text-xl">{indicator.name}</span>
                          </span>
                          <div className="flex-shrink-0 flex items-center justify-end text-right min-w-[65px] ml-4">
                            <div className="flex items-center gap-2 w-full">
                              <div className="flex-shrink-0 flex items-center justify-end text-right min-w-[65px]">
                                <span className="flex flex-row items-center gap-1 text-[#2DE282] font-bold text-base sm:text-base lg:text-lg" style={{ textShadow: '0 0 2px #000, 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000' }}>
                                  {indicator.max && indicator.max > 0 ? `${Math.round(100 * indicator.value / indicator.max)}%` : '0%'}
                                  <span className="text-[#2DE282] font-bold">({indicator.value}/{indicator.max})</span>
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </>
                  )}
                </div>
              </div>
            </div>
            {/* Social Indicators */}
            <div className="flex-1">
              <div className="flex justify-between items-center mb-2 mt-4 sm:mt-6 lg:mt-10">
                <span className="uppercase font-bold text-[#FF6A00] text-base sm:text-lg lg:text-xl px-2 sm:px-3">Social Indicators</span>
                <span className="font-bold text-[#2DE282] text-base sm:text-base lg:text-lg text-right px-2 sm:px-3">Score: {(() => {
                  const score = socialIndicators.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
                  const max = socialIndicators.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
                  return max > 0 ? `${score}/${max} pts` : '0 pts';
                })()}</span>
              </div>
              <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-4">
                <div className="space-y-3">
                  {loading ? (
                    <div className="text-center text-[#FF6A00] py-4">Loading...</div>
                  ) : (
                    <>
                      {socialIndicators.map((indicator, idx) => (
                        <div key={indicator.name} className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                          <span className="flex items-center gap-2">
                            {indicator.name === 'Social Volume' && <span>👥</span>}
                            {indicator.name === 'Sentiment Analysis' && <span>😊</span>}
                            {indicator.name === 'Developer Activity' && <span>📈</span>}
                            <span className="text-[#FF6A00] font-bold text-base sm:text-lg lg:text-xl">{indicator.name}</span>
                          </span>
                          <div className="flex-shrink-0 flex items-center justify-end text-right min-w-[65px] ml-4">
                            <div className="flex items-center gap-2 w-full">
                              <div className="flex-shrink-0 flex items-center justify-end text-right min-w-[65px]">
                                <span className="flex flex-row items-center gap-1 text-[#2DE282] font-bold text-base sm:text-base lg:text-lg" style={{ textShadow: '0 0 2px #000, 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000' }}>
                                  {indicator.max && indicator.max > 0 ? `${Math.round(100 * indicator.value / indicator.max)}%` : '0%'}
                                  <span className="text-[#2DE282] font-bold">({indicator.value}/{indicator.max})</span>
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Modal Overlay */}
        {showCronjobs && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
            <div className="bg-[#232323] rounded-2xl shadow-xl p-6 w-full max-w-2xl relative animate-fade-in">
              <button
                className="absolute top-3 right-4 text-[#FF6A00] text-2xl font-bold hover:text-[#FFA64D] focus:outline-none"
                onClick={() => setShowCronjobs(false)}
                aria-label="Close"
              >
                ×
              </button>
              <h2 className="text-[#FF6A00] text-xl font-bold mb-4">Cronjobs</h2>
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
                          {(() => {
                            // Custom cron to CET/CEST converter
                            try {
                              const parts = job.schedule.split(' ');
                              if (parts.length < 5) throw new Error('Invalid cron format');
                              const [min, hour, day, month] = parts;
                              const utcDate = new Date(Date.UTC(
                                new Date().getFullYear(), // Use current year
                                parseInt(month) - 1,
                                parseInt(day),
                                parseInt(hour),
                                parseInt(min)
                              ));
                              const formatter = new Intl.DateTimeFormat('de-DE', {
                                timeZone: 'Europe/Berlin',
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: false,
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric'
                              });
                              return formatter.format(utcDate) + ' CET';
                            } catch (e) {
                              return job.schedule;
                            }
                          })()}
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

