import React, { FC } from 'react';

interface ScoreDisplayProps {
  score: number;
  recommendation: string;
  recommendationDesc: string;
  selectedToken: string;
  futures?: boolean;
}

/**
 * Component for displaying score and recommendation
 */
const ScoreDisplay: FC<ScoreDisplayProps> = ({ 
  score, 
  recommendation, 
  recommendationDesc,
  selectedToken,
  futures = false
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
      
      <div className="w-full flex flex-row items-center justify-center gap-4 mt-2">
        <a
          href={`https://www.mexc.com/de-DE/exchange/${selectedToken}_USDT`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[#2DE282] underline text-base sm:text-base lg:text-lg hover:text-[#FF6A00] transition-colors text-center"
          style={{ display: 'inline-block' }}
        >
          MEXC Spot
        </a>
        {futures && (
          <a
            href={`https://www.mexc.com/de-DE/futures/overview?symbol=${selectedToken}_USDT`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#2DE282] underline text-base sm:text-base lg:text-lg hover:text-[#FF6A00] transition-colors text-center"
            style={{ display: 'inline-block' }}
          >
            MEXC Futures
          </a>
        )}
      </div>
    </div>
  );
};

export default ScoreDisplay;
