import React, { FC } from 'react';
import { IndicatorList, Indicator } from './IndicatorList';

interface IndicatorSectionProps {
  title: string;
  indicators: Indicator[];
  loading: boolean;
}

/**
 * Component for displaying a section of indicators with title and score
 */
const IndicatorSection: FC<IndicatorSectionProps> = ({ 
  title, 
  indicators, 
  loading 
}) => {
  // Calculate score
  const score = indicators.reduce((sum, i) => sum + (typeof i.value === 'number' ? i.value : 0), 0);
  const max = indicators.reduce((sum, i) => sum + (typeof i.max === 'number' ? i.max : 0), 0);
  const formattedScore = max > 0 ? `${score.toFixed(1)}/${max}` : '0';

  return (
    <div>
      <div className="flex justify-between items-center mb-2 mt-4">
        <span className="uppercase text-[#FF6A00] text-base sm:text-lg lg:text-xl px-2 sm:px-3">
          {title}
        </span>
        <span className="text-[#2DE282] text-base sm:text-base lg:text-lg text-right px-2 sm:px-3">
          {formattedScore}
        </span>
      </div>
      <div className="bg-[#242424] rounded-2xl p-4 sm:p-6 mt-2">
        <IndicatorList indicators={indicators} loading={loading} />
      </div>
    </div>
  );
};

export default IndicatorSection;
