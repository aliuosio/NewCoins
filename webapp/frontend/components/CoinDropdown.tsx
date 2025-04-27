import React, { FC } from 'react';

interface CoinDropdownProps {
  selectedToken: string;
  analysedCoins: string[];
  onSelect: (token: string) => void;
  onToggleDropdown: () => void;
  showDropdown: boolean;
  loading: boolean;
}

/**
 * Dropdown component for selecting a coin
 */
const CoinDropdown: FC<CoinDropdownProps> = ({ 
  selectedToken, 
  analysedCoins, 
  onSelect, 
  onToggleDropdown, 
  showDropdown, 
  loading 
}) => {
  return (
    <div className="relative w-full max-w-[220px]">
      <button
        className="w-full bg-[#242424] text-[#2DE282] text-base sm:text-lg rounded-lg px-4 py-2 flex items-center justify-center focus:outline-none border-2 border-transparent focus:border-transparent hover:border-transparent active:border-transparent transition-colors"
        style={{ minHeight: '44px' }}
        onClick={onToggleDropdown}
        type="button"
        disabled={loading}
      >
        <span className="flex items-center justify-center gap-2 w-full">
          {selectedToken || 'Select Coin'}
          <svg 
            className="w-4 h-4 text-[#2DE282]" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </button>
      
      {showDropdown && (
        <div className="absolute z-10 w-full coin-dropdown-menu rounded-lg shadow-lg mt-2 max-h-60 overflow-auto border border-[#333]">
          {analysedCoins.map(symbol => (
            <div
              key={symbol}
              className={`w-full px-4 py-2 text-base sm:text-lg flex items-center justify-center cursor-pointer rounded-lg transition-colors ${
                symbol === selectedToken 
                  ? 'bg-[#333] text-[#2DE282]' 
                  : 'text-[#FF6A00] hover:bg-[#222] active:bg-[#222]'
              }`}
              style={{ minHeight: '44px' }}
              onClick={() => { onSelect(symbol); onToggleDropdown(); }}
            >
              {symbol}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CoinDropdown;
