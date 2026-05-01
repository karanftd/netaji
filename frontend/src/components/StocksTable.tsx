import React from 'react';
import { Briefcase } from 'lucide-react';

interface Stock {
  id: string;
  company_name: string;
  quantity: number | null;
  rate: number | null;
  total_value: number;
}

interface StocksTableProps {
  stocks: Stock[];
}

const StocksTable: React.FC<StocksTableProps> = ({ stocks }) => {
  if (!stocks || stocks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 bg-gray-50/50 dark:bg-gray-900/30 rounded-2xl border-2 border-dashed border-gray-200 dark:border-gray-700">
        <Briefcase className="h-12 w-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h4 className="text-lg font-medium text-gray-900 dark:text-white">No stock investments found</h4>
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center mt-1">
          This politician does not have any direct equity holdings listed in their affidavit.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
        <thead className="bg-gray-50/50 dark:bg-gray-900/50">
          <tr>
            <th className="px-8 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">
              Company Name
            </th>
            <th className="px-8 py-4 text-right text-xs font-bold text-gray-400 uppercase tracking-widest">
              Quantity
            </th>
            <th className="px-8 py-4 text-right text-xs font-bold text-gray-400 uppercase tracking-widest">
              Rate
            </th>
            <th className="px-8 py-4 text-right text-xs font-bold text-gray-400 uppercase tracking-widest">
              Total Value
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-100 dark:divide-gray-700">
          {stocks.map((stock) => (
            <tr key={stock.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-700/50 transition-colors">
              <td className="px-8 py-6 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-white">
                {stock.company_name}
              </td>
              <td className="px-8 py-6 whitespace-nowrap text-sm text-right text-gray-600 dark:text-gray-400">
                {stock.quantity?.toLocaleString() || '-'}
              </td>
              <td className="px-8 py-6 whitespace-nowrap text-sm text-right text-gray-600 dark:text-gray-400">
                {stock.rate ? `₹${stock.rate.toLocaleString('en-IN')}` : '-'}
              </td>
              <td className="px-8 py-6 whitespace-nowrap text-sm text-right font-bold text-indigo-600 dark:text-indigo-400">
                ₹{stock.total_value.toLocaleString('en-IN')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StocksTable;
