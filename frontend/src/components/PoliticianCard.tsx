import React from 'react';

interface PoliticianCardProps {
  politician: {
    id: string;
    name: string;
    party: string;
    constituency: string;
    state: string;
    total_assets: number;
  };
  onClick: () => void;
}

const PoliticianCard: React.FC<PoliticianCardProps> = ({ politician, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer border border-gray-100 dark:border-gray-700"
    >
      <div className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
              {politician.name}
            </h3>
            <p className="text-sm text-indigo-600 dark:text-indigo-400 font-medium">
              {politician.party}
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded">
              {politician.state}
            </span>
          </div>
        </div>
        
        <div className="mt-4">
          <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Constituency
          </p>
          <p className="text-sm text-gray-700 dark:text-gray-300">
            {politician.constituency}
          </p>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Declared Wealth
          </p>
          <p className="text-lg font-bold text-green-600 dark:text-green-400">
            ₹{(politician.total_assets / 10000000).toFixed(2)} Cr
          </p>
        </div>
      </div>
    </div>
  );
};

export default PoliticianCard;
