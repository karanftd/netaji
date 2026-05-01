import React from 'react';

interface Investment {
  type: string;
  amount: number;
  description: string;
}

interface InvestmentsTableProps {
  investments: Investment[];
}

const InvestmentsTable: React.FC<InvestmentsTableProps> = ({ investments }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
        <thead className="bg-gray-50/50 dark:bg-gray-900/50">
          <tr>
            <th className="px-8 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">
              Category
            </th>
            <th className="px-8 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">
              Description
            </th>
            <th className="px-8 py-4 text-right text-xs font-bold text-gray-400 uppercase tracking-widest">
              Amount
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-100 dark:divide-gray-700">
          {investments.map((inv, index) => (
            <tr key={index} className="hover:bg-gray-50/50 dark:hover:bg-gray-700/50 transition-colors">
              <td className="px-8 py-6 whitespace-nowrap text-sm font-semibold text-indigo-600 dark:text-indigo-400">
                {inv.type}
              </td>
              <td className="px-8 py-6 text-sm text-gray-600 dark:text-gray-300 max-w-md truncate">
                {inv.description}
              </td>
              <td className="px-8 py-6 whitespace-nowrap text-sm text-right font-bold text-gray-900 dark:text-white">
                ₹{inv.amount.toLocaleString('en-IN')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default InvestmentsTable;
