import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts';
import { TrendingUp, Users, PieChart as PieIcon, ArrowLeft, Loader2, BarChart as BarChartIcon } from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'];

const Analytics: React.FC = () => {
  const [richest, setRichest] = useState([]);
  const [partyWealth, setPartyWealth] = useState([]);
  const [popularStocks, setPopularStocks] = useState([]);
  const [partyStocks, setPartyStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const [rRes, pRes, sRes, psRes] = await Promise.all([
          axios.get('http://localhost:5000/api/analytics/richest'),
          axios.get('http://localhost:5000/api/analytics/party-wealth'),
          axios.get('http://localhost:5000/api/analytics/popular-stocks'),
          axios.get('http://localhost:5000/api/analytics/party-stock-stats')
        ]);
        setRichest(rRes.data);
        setPartyWealth(pRes.data);
        setPopularStocks(sRes.data);
        setPartyStocks(psRes.data);
      } catch (error) {
        console.error("Failed to fetch analytics", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  const formatCurrency = (value: number) => {
    return `₹${(value / 10000000).toFixed(2)} Cr`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-12 w-12 text-indigo-600 animate-spin" />
          <p className="text-gray-500 dark:text-gray-400 font-medium">Analyzing wealth declarations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 pb-20">
      <nav className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10 border-b border-gray-100 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => window.location.href = '/dashboard'}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
              >
                <ArrowLeft className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              </button>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">Netaji Analytics</h1>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Richest Politicians */}
          <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
            <div className="flex items-center space-x-3 mb-8">
              <TrendingUp className="h-6 w-6 text-indigo-600" />
              <h3 className="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wider">Richest Politicians</h3>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={richest} layout="vertical" margin={{ left: 40, right: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e5e7eb" opacity={0.5} />
                  <XAxis type="number" hide />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    width={120} 
                    tick={{ fontSize: 11 }}
                    tickFormatter={(val) => val.length > 15 ? `${val.substring(0, 15)}...` : val}
                  />
                  <Tooltip 
                    formatter={(value: any) => formatCurrency(value)}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                  />
                  <Bar dataKey="total_assets" radius={[0, 4, 4, 0]}>
                    {richest.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Party Wealth Distribution */}
          <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
            <div className="flex items-center space-x-3 mb-8">
              <Users className="h-6 w-6 text-emerald-600" />
              <h3 className="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wider">Party-wise Wealth</h3>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={partyWealth}
                    dataKey="total_assets"
                    nameKey="party"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                  >
                    {partyWealth.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any) => formatCurrency(value)} />
                  <Legend verticalAlign="bottom" align="center" iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Party-wise Stock Holdings */}
          <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
            <div className="flex items-center space-x-3 mb-8">
              <BarChartIcon className="h-6 w-6 text-indigo-600" />
              <h3 className="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wider">Stocks by Party</h3>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={partyStocks} layout="vertical" margin={{ left: 40, right: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e5e7eb" opacity={0.5} />
                  <XAxis type="number" hide />
                  <YAxis 
                    dataKey="party" 
                    type="category" 
                    width={100} 
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip 
                    formatter={(value: any) => [`${value} Holdings`, 'Count']}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} name="Holdings">
                    {partyStocks.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Popular Stocks */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
            <div className="flex items-center space-x-3 mb-8">
              <PieIcon className="h-6 w-6 text-amber-600" />
              <h3 className="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wider">Most Common Stocks Between Politicians</h3>
            </div>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={popularStocks}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" opacity={0.5} />
                  <XAxis 
                    dataKey="company" 
                    tick={{ fontSize: 10 }} 
                    angle={-45} 
                    textAnchor="end" 
                    height={120}
                  />
                  <YAxis tick={{ fontSize: 11 }} label={{ value: 'No. of Politicians', angle: -90, position: 'insideLeft' }} />
                  <Tooltip 
                    cursor={{ fill: 'transparent' }}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                    formatter={(value: any, name: string, props: any) => {
                      if (name === "No. of Politicians") return [value, name];
                      return [`₹${(props.payload.total_value / 10000000).toFixed(2)} Cr`, "Total Aggregated Value"];
                    }}
                  />
                  <Bar dataKey="count" name="No. of Politicians" fill="#4f46e5" radius={[4, 4, 0, 0]} barSize={40}>
                    {popularStocks.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
};

export default Analytics;
