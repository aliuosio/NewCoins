import React, { FC } from 'react';
import { formatCronjobDate } from '../utils/formatCronjobDate';

interface Cronjob {
  id: number;
  schedule: string;
  command: string;
  _sortDate?: Date | null;
}

interface CronjobsModalProps {
  isOpen: boolean;
  onClose: () => void;
  cronjobs: Cronjob[];
  loading: boolean;
}

/**
 * Modal component for displaying cronjobs
 */
const CronjobsModal: FC<CronjobsModalProps> = ({ 
  isOpen, 
  onClose, 
  cronjobs, 
  loading 
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
      <div className="bg-[#232323] rounded-2xl shadow-xl p-6 w-full max-w-2xl relative animate-fade-in">
        <button
          className="absolute top-3 right-4 text-[#FF6A00] text-2xl hover:text-[#FFA64D] focus:outline-none"
          onClick={onClose}
          aria-label="Close"
        >
          ×
        </button>
        <h2 className="text-[#FF6A00] text-xl mb-4">Cronjobs</h2>
        <div className="text-[#FFDEB4] text-sm">
          {loading ? (
            <div className="py-4 text-center">Loading...</div>
          ) : cronjobs.length === 0 ? (
            <div className="py-4 text-center">No cronjobs found.</div>
          ) : (
            <ul className="space-y-2">
              {cronjobs.map(job => (
                <li key={job.id} className="flex justify-between items-center bg-[#292929] rounded-lg px-4 py-2">
                  <span className="text-[#2DE282] font-semibold w-1/3 text-base sm:text-lg">
                    {formatCronjobDate(job.schedule)}
                  </span>
                  <span className="text-white break-all w-2/3 text-center text-base sm:text-lg">
                    {job.command.replace('/usr/bin/python -m', '').replace('Trade.main', '').replace('Trade.pre_trade', 'pretrade').trim()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default CronjobsModal;
