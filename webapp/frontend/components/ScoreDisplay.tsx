import React, { FC } from 'react';

interface ScoreDisplayProps {
  score: number;
  recommendation: string;
  recommendationDesc: string;
  selectedToken: string;
}

/**
 * Component for displaying score and recommendation
 */
const ScoreDisplay: FC<ScoreDisplayProps> = ({ 
  score, 
  recommendation, 
  recommendationDesc,
  selectedToken
}) => {
  // Map recommendation to color classes
  const recommendationColor = {
    'STRONG BUY': 'text-[#2DE282]', // bright green
    'BUY': 'text-[#00FFB2]',       // teal
    'HOLD': 'text-[#FFD600]',      // yellow
    'WATCH': 'text-[#FF6A00]',     // orange
    'AVOID': 'text-[#FF3B3B]',     // red
    '': 'text-[#888888]'           // gray for no label
  };

  const colorClass = recommendationColor[recommendation] || 'text-[#2DE282]';

  return (
    <div className="flex flex-col items-center justify-center flex-1 gap-2 mx-2 text-center">
      <span 
        className={`text-2xl sm:text-3xl lg:text-5xl text-center mx-auto ${colorClass}`}
        style={{ textShadow: '0 0 2px #000, 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000' }}
      >
        {Math.floor(score)}%
      </span>
      
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
  );
};

export default ScoreDisplay;
