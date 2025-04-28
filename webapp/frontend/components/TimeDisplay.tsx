import React, { FC } from 'react';

interface TimeDisplayProps {
  timestamp: string | null;
  className?: string;
}

/**
 * Component for displaying formatted timestamps
 */
const TimeDisplay: FC<TimeDisplayProps> = ({ timestamp, className = '' }) => {
  if (!timestamp) return null;

  // Parse the timestamp as a Date in Europe/Berlin timezone
  const eventDate = new Date(timestamp);

  // Get the current time in Europe/Berlin
  const berlinNow = new Date(new Date().toLocaleString('en-US', { timeZone: 'Europe/Berlin' }));

  const formattedTime = eventDate.toLocaleString('de-DE', {
    timeZone: 'Europe/Berlin',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });

  const isFuture = eventDate.getTime() > berlinNow.getTime();
  const colorClass = isFuture ? 'text-[#2DE282]' : 'text-[#FF6A00]';

  return (
    <div className={`text-base sm:text-base lg:text-lg ${className}`}>
      <span className={colorClass}>{formattedTime}</span>
    </div>
  );
};

export default TimeDisplay;
