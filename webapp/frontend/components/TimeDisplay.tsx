import React, { FC } from 'react';

interface TimeDisplayProps {
  label: string;
  timestamp: string | null;
  className?: string;
}

/**
 * Component for displaying formatted timestamps
 */
const TimeDisplay: FC<TimeDisplayProps> = ({ label, timestamp, className = '' }) => {
  if (!timestamp) return null;
  
  const formattedTime = new Date(timestamp).toLocaleString('de-DE', {
    timeZone: 'Europe/Berlin',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });

  return (
    <div className={`text-[#2DE282] text-base sm:text-base lg:text-lg ${className}`}>
      {label}: {formattedTime}
    </div>
  );
};

export default TimeDisplay;
