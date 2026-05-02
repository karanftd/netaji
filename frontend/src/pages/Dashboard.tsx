import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import PoliticianCard from '../components/PoliticianCard';
import InvestmentsTable from '../components/InvestmentsTable';
import StocksTable from '../components/StocksTable';
import AssetChart from '../components/AssetChart';
import ThemeToggle from '../components/ThemeToggle';
import { Search, X, TrendingUp, Landmark, ShieldCheck, PieChart as PieChartIcon, LayoutList } from 'lucide-react';

interface Politician {
  id: string;
  name: string;
  party: string;
  constituency: string;
  state: string;
  total_assets: number;
  investments: any[];
  stocks?: any[];
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [politicians, setPoliticians] = useState<Politician[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedPolitician, setSelectedPolitician] = useState<Politician | null>(null);
  const [fetchingDetails, setFetchingDetails] = useState(false);
  const [activeTab, setActiveTab] = useState<'general' | 'stocks'>('general');

  useEffect(() => {
    fetchPoliticians();
  }, []);

  const fetchPoliticians = async (query = '') => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/politicians${query ? `?q=${query}` : ''}`);
      setPoliticians(response.data);
    } catch (error) {
      console.error("Failed to fetch politicians", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPoliticianDetails = async (politician: Politician) => {
    setFetchingDetails(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/politicians/${politician.id}`);
      setSelectedPolitician(response.data);
    } catch (error) {
      console.error("Failed to fetch politician details", error);
      // Fallback to what we have if API fails
      setSelectedPolitician(politician);
    } finally {
      setFetchingDetails(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPoliticians(search);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <nav className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10 border-b border-gray-100 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex-shrink-0 flex items-center">
              <TrendingUp className="h-6 w-6 text-indigo-600 dark:text-indigo-400 mr-2" />
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400">
                Netaji
              </h1>
            </div>
            <div className="flex items-center space-x-6">
              <ThemeToggle />
              <div className="hidden sm:flex items-center space-x-2">
                <img 
                  src={user?.photoURL || ''} 
                  alt={user?.displayName || ''} 
                  className="h-8 w-8 rounded-full border-2 border-indigo-100 dark:border-indigo-900"
                />
                <span className="text-gray-700 dark:text-gray-300 text-sm font-medium">
                  {user?.displayName}
                </span>
              </div>
              <button
                onClick={logout}
                className="text-sm font-semibold text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
        {fetchingDetails ? (
          <div className="flex flex-col justify-center items-center h-96 space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            <p className="text-gray-500 dark:text-gray-400 animate-pulse">Loading detailed financial records...</p>
          </div>
        ) : !selectedPolitician ? (
          <>
            <div className="text-center mb-12">
              <h2 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-4 tracking-tight">
                Politician Wealth Dashboard
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-8">
                Search through official affidavits and discover where India's representatives are investing their wealth.
              </p>
              
              <form onSubmit={handleSearch} className="max-w-2xl mx-auto relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                </div>
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search by name, party, or state..."
                  className="w-full pl-12 pr-4 py-4 rounded-2xl border-2 border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-xl focus:border-indigo-500 dark:focus:border-indigo-500 outline-none transition-all text-lg"
                />
              </form>
            </div>

            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : (
              <div className="grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                {politicians.map((p) => (
                  <PoliticianCard 
                    key={p.id} 
                    politician={p} 
                    onClick={() => fetchPoliticianDetails(p)} 
                  />
                ))}
              </div>
            )}
            
            {!loading && politicians.length === 0 && (
              <div className="text-center py-20 bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700">
                <p className="text-gray-500 dark:text-gray-400 text-lg">No politicians found matching your search.</p>
              </div>
            )}
          </>
        ) : (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <button 
              onClick={() => setSelectedPolitician(null)}
              className="flex items-center text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 mb-8 transition-colors group"
            >
              <X className="h-5 w-5 mr-2 group-hover:rotate-90 transition-transform" />
              Back to Dashboard
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Profile Card */}
              <div className="lg:col-span-1 space-y-8">
                <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
                  <div className="flex items-center space-x-4 mb-6">
                    <div className="h-16 w-16 bg-indigo-100 dark:bg-indigo-900 rounded-2xl flex items-center justify-center text-indigo-600 dark:text-indigo-400 text-2xl font-bold">
                      {selectedPolitician.name.charAt(0)}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white leading-tight">
                        {selectedPolitician.name}
                      </h2>
                      <p className="text-indigo-600 dark:text-indigo-400 font-semibold">
                        {selectedPolitician.party}
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Landmark className="h-4 w-4 mr-3" />
                      <span className="text-sm">{selectedPolitician.constituency}, {selectedPolitician.state}</span>
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <ShieldCheck className="h-4 w-4 mr-3" />
                      <span className="text-sm">Verified Affidavit Data</span>
                    </div>
                  </div>

                  <div className="mt-8 pt-8 border-t border-gray-100 dark:border-gray-700">
                    <p className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-widest font-bold mb-1">
                      Total Assets
                    </p>
                    <p className="text-4xl font-extrabold text-green-600 dark:text-green-400">
                      ₹{(selectedPolitician.total_assets / 10000000).toFixed(2)} Cr
                    </p>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 p-8">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Asset Distribution</h3>
                  <AssetChart data={Object.entries(
                    selectedPolitician.investments.reduce((acc, inv) => {
                      let type = inv.type;
                      // Shorten long labels for the chart
                      if (type.includes('Deposits')) type = 'Bank Deposits';
                      if (type.includes('Bonds') || type.includes('Shares')) type = 'Stocks & Bonds';
                      if (type.includes('Insurance') || type.includes('LIC')) type = 'Insurance';
                      if (type.includes('Jewellery')) type = 'Jewellery';
                      if (type.includes('Motor Vehicles')) type = 'Vehicles';
                      if (type.includes('Personal loans')) type = 'Loans Given';
                      
                      acc[type] = (acc[type] || 0) + inv.amount;
                      return acc;
                    }, {} as Record<string, number>)
                  ).map(([name, value]) => ({ name, value }))} />
                </div>
              </div>

              {/* Detailed Investments */}
              <div className="lg:col-span-2">
                <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                  <div className="px-8 pt-8 border-b border-gray-100 dark:border-gray-700">
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        Portfolio Details
                      </h3>
                    </div>
                    
                    {/* Tabs */}
                    <div className="flex space-x-8">
                      <button
                        onClick={() => setActiveTab('general')}
                        className={`pb-4 text-sm font-bold tracking-widest uppercase transition-colors relative ${
                          activeTab === 'general' 
                            ? 'text-indigo-600 dark:text-indigo-400' 
                            : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                        }`}
                      >
                        General Investments
                        {activeTab === 'general' && (
                          <div className="absolute bottom-0 left-0 right-0 h-1 bg-indigo-600 dark:bg-indigo-400 rounded-t-full" />
                        )}
                      </button>
                      <button
                        onClick={() => setActiveTab('stocks')}
                        className={`pb-4 text-sm font-bold tracking-widest uppercase transition-colors relative ${
                          activeTab === 'stocks' 
                            ? 'text-indigo-600 dark:text-indigo-400' 
                            : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                        }`}
                      >
                        Equity Portfolio
                        {activeTab === 'stocks' && (
                          <div className="absolute bottom-0 left-0 right-0 h-1 bg-indigo-600 dark:bg-indigo-400 rounded-t-full" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="p-0">
                    {activeTab === 'general' ? (
                      <InvestmentsTable investments={selectedPolitician.investments} />
                    ) : (
                      <StocksTable stocks={selectedPolitician.stocks || []} />
                    )}
                  </div>
                  
                  <div className="p-8 bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400">
                    * Data extracted from official election nomination papers. Values shown are at the time of filing.
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
