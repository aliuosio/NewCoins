import React, { useState } from 'react';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], weight: ['400', '600', '700'] });

export default function Home() {
  const [selectedToken, setSelectedToken] = useState('BTC');
  const [showCronjobs, setShowCronjobs] = useState(false);
  return (
    <>
      <div className="min-h-screen flex items-center justify-center bg-[#121212] font-inter px-2 sm:px-4">
        <div className="bg-[#1A1A1A] text-[#FF6A00] rounded-2xl p-4 sm:p-6 md:p-8 lg:p-12 w-full max-w-[98vw] sm:max-w-[400px] md:max-w-[520px] lg:max-w-[700px] shadow-lg">
        {/* Header */}
        <div className="flex justify-between items-center mb-10 lg:mb-14">
          <select
  className="bg-[#242424] text-[#FF6A00] px-3 py-1.5 sm:px-4 sm:py-2 lg:px-6 lg:py-3 rounded-lg font-bold text-sm sm:text-base lg:text-xl appearance-none focus:outline-none focus:ring-2 focus:ring-[#FF6A00] cursor-pointer"
  value={selectedToken}
  onChange={e => setSelectedToken(e.target.value)}
>
  <option value="BTC">BTC</option>
  <option value="ETH">ETH</option>
  <option value="SOL">SOL</option>
  <option value="DOGE">DOGE</option>
</select>
          <button
  className="text-[#FF6A00] font-semibold text-xs sm:text-sm lg:text-lg hover:text-[#FFA64D] cursor-pointer bg-transparent border-none outline-none"
  onClick={() => setShowCronjobs(true)}
>
  Cronjobs
</button>
        </div>

        {/* Technical Indicators */}
        <div className="uppercase font-bold text-xs sm:text-sm lg:text-base mb-2 mt-6">Technical Indicators</div>
        <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-6">
          <div className="space-y-3">
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-1 sm:gap-2 lg:gap-4"><span>📈</span>Trading Volume</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '90%' }}></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-2"><span>💼</span>Liquidity</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '85%' }}></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-2"><span>🔁</span>Whale Transactions</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '70%' }}></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-2"><span>📊</span>Token Distribution</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '40%' }}></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-2"><span>🛡️</span>Pre-Sale Vesting</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '50%' }}></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-2"><span>📝</span>Smart Contract Audit</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '30%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Social Indicators */}
        <div className="uppercase font-bold text-xs sm:text-sm lg:text-base mb-2 mt-4 sm:mt-6 lg:mt-10">Social Indicators</div>
        <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-4">
          <div className="space-y-3">
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-2"><span>👥</span>Social Volume</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '75%' }}></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-2"><span>😊</span>Sentiment Analysis</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '65%' }}></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
              <span className="flex items-center gap-2"><span>📈</span>Developer Activity</span>
              <div className="w-1/2 progress-track ml-4">
                <div className="progress-bar" style={{ width: '45%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Recommendation */}
        <div className="border-t border-[#2D2D2D] mt-4 sm:mt-6 lg:mt-10 pt-4">
  <div className="flex items-center justify-between gap-4 w-full">
  <div className="text-2xl sm:text-3xl lg:text-5xl font-bold text-[#FF6A00]">82%</div>
  <div className="flex items-center gap-3">
    <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#FF6A00]">Total</div>
    <div className="bg-[#2DE282] text-black font-bold text-xs sm:text-sm lg:text-lg px-3 py-2 sm:px-4 lg:px-8 lg:py-3 rounded-lg glow-button flex items-center h-full">
      STRONG BUY
    </div>
  </div>
</div>
  <div className="text-[#00FFB2] text-xs sm:text-sm lg:text-base mt-2">High potential for growth</div>
</div>
      {/* Cronjobs Modal */}
      {showCronjobs && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
          <div className="bg-[#232323] rounded-2xl shadow-xl p-6 w-full max-w-md relative animate-fade-in">
            <button
              className="absolute top-3 right-4 text-[#FF6A00] text-2xl font-bold hover:text-[#FFA64D] focus:outline-none"
              onClick={() => setShowCronjobs(false)}
            >
              Cronjobs
            </button>
          </div>

          {/* Technical Indicators */}
          <div className="uppercase font-bold text-xs sm:text-sm lg:text-base mb-2 mt-6">Technical Indicators</div>
          <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-6">
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-1 sm:gap-2 lg:gap-4"><span>📈</span>Trading Volume</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '90%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-2"><span>💼</span>Liquidity</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '85%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-2"><span>🔁</span>Whale Transactions</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '70%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-2"><span>📊</span>Token Distribution</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '40%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-2"><span>🛡️</span>Pre-Sale Vesting</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '50%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-2"><span>📝</span>Smart Contract Audit</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '30%' }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Social Indicators */}
          <div className="uppercase font-bold text-xs sm:text-sm lg:text-base mb-2 mt-4 sm:mt-6 lg:mt-10">Social Indicators</div>
          <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-2"><span>👥</span>Social Volume</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '75%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-2"><span>😊</span>Sentiment Analysis</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '65%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
                <span className="flex items-center gap-2"><span>📈</span>Developer Activity</span>
                <div className="w-1/2 progress-track ml-4">
                  <div className="progress-bar" style={{ width: '45%' }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="border-t border-[#2D2D2D] mt-4 sm:mt-6 lg:mt-10 pt-4">
            <div className="flex items-center justify-between gap-4 w-full">
              <div className="text-2xl sm:text-3xl lg:text-5xl font-bold text-[#FF6A00]">82%</div>
              <div className="flex items-center gap-3">
                <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#FF6A00]">Total</div>
                <div className="bg-[#2DE282] text-black font-bold text-xs sm:text-sm lg:text-lg px-3 py-2 sm:px-4 lg:px-8 lg:py-3 rounded-lg glow-button flex items-center h-full">
                  STRONG BUY
                </div>
              </div>
            </div>
            <div className="text-[#00FFB2] text-xs sm:text-sm lg:text-base mt-2">High potential for growth</div>
          </div>
        </div>

        {/* Cronjobs Modal */}
        {showCronjobs && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
            <div className="bg-[#232323] rounded-2xl shadow-xl p-6 w-full max-w-md relative animate-fade-in">
              <button
                className="absolute top-3 right-4 text-[#FF6A00] text-2xl font-bold hover:text-[#FFA64D] focus:outline-none"
                onClick={() => setShowCronjobs(false)}
                aria-label="Close"
              >
                ×
              </button>
              <h2 className="text-[#FF6A00] text-xl font-bold mb-4">Cronjobs</h2>
              <div className="text-[#FFDEB4] text-sm">
                <ul className="space-y-2">
                  <li className="flex justify-between items-center bg-[#292929] rounded-lg px-4 py-2">
                    <span>Update Prices</span>
                    <span className="text-[#2DE282] font-semibold">Every 5 min</span>
                  </li>
                  <li className="flex justify-between items-center bg-[#292929] rounded-lg px-4 py-2">
                    <span>Fetch Social Data</span>
                    <span className="text-[#2DE282] font-semibold">Hourly</span>
                  </li>
                  <li className="flex justify-between items-center bg-[#292929] rounded-lg px-4 py-2">
                    <span>Analyze Whale Tx</span>
                    <span className="text-[#2DE282] font-semibold">Daily</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

  );
}
