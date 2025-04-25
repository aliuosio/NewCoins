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
        <div key={indicator.name} className="flex flex-col text-sm rounded-lg px-2 sm:px-3 py-1 mb-1">
          <div className="flex items-center">
            <span className="flex items-center gap-2">
              {iconMap[indicator.name]}
              <span className="text-[#FF6A00] text-sm sm:text-base lg:text-lg">{indicator.name}</span>
            </span>
          </div>
          <div className="mt-0.5 ml-8 flex flex-row items-center gap-2 text-[#2DE282]">
            <span className="text-sm sm:text-base lg:text-lg">
              {indicator.value.toFixed(2)}/{indicator.max}
            </span>
            <span className="text-sm sm:text-base lg:text-lg" style={{ textShadow: '0 0 2px #000, 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000' }}>
              {indicator.max && indicator.max > 0 ? `${Math.round(100 * indicator.value / indicator.max)}%` : '0%'}
            </span>
          </div>
        </div>
      ))}
    </>
  );
};
