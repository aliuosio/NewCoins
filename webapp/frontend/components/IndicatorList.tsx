import React from 'react';

export interface Indicator {
  name: string;
  value: number;
  max: number;
}

interface IndicatorListProps {
  indicators: Indicator[];
  loading: boolean;
}

const iconMap: Record<string, React.ReactNode> = {
  'Trading Volume': <span>📊</span>,
  'Liquidity': <span>💧</span>,
  'Whale Transactions': <span>🐳</span>,
  'Token Distribution': <span>📈</span>,
  'Pre-Sale Vesting': <span>📆</span>,
  'Smart Contract Audit': <span>📝</span>,
  'Social Volume': <span>👥</span>,
  'Sentiment Analysis': <span>😊</span>,
  'Developer Activity': <span>📈</span>,
};

export const IndicatorList: React.FC<IndicatorListProps> = ({ indicators, loading }) => {
  if (loading) {
    return <div className="text-center text-[#FF6A00] py-4">Loading...</div>;
  }
  return (
    <>
      {indicators.map((indicator) => (
        <div key={indicator.name} className="flex justify-between items-center text-sm rounded-lg px-2 sm:px-3 py-1 mb-0.5">
          <span className="flex items-center gap-2">
            {iconMap[indicator.name]}
            <span className="text-[#FF6A00] font-bold text-base sm:text-lg lg:text-xl">{indicator.name}</span>
          </span>
          <div className="flex-shrink-0 flex items-center justify-end text-right min-w-[65px] ml-4">
            <div className="flex items-center gap-2 w-full">
              <div className="flex-shrink-0 flex items-center justify-end text-right min-w-[65px]">
                <span className="flex flex-row items-center gap-1 text-[#2DE282] font-bold text-base sm:text-base lg:text-lg" style={{ textShadow: '0 0 2px #000, 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000' }}>
                  {indicator.max && indicator.max > 0 ? `${Math.round(100 * indicator.value / indicator.max)}%` : '0%'}
                  <span className="text-[#2DE282] font-bold">({indicator.value.toFixed(2)}/{indicator.max})</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </>
  );
};
