import React, { useEffect, useState } from 'react';
import api, { endpoints } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { AlertCircle, TrendingUp, Users, Wallet, Filter } from 'lucide-react';

const StatCard = ({ title, value, subtext, icon: Icon, color }) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
        <div className="flex items-start justify-between">
            <div>
                <p className="text-sm font-medium text-slate-500">{title}</p>
                <h3 className="text-2xl font-bold text-slate-900 mt-2">{value}</h3>
                {subtext && <p className="text-xs text-slate-400 mt-1">{subtext}</p>}
            </div>
            <div className={`p-3 rounded-lg ${color}`}>
                <Icon size={24} className="text-white" />
            </div>
        </div>
    </div>
);

const Dashboard = () => {
    const [loanStats, setLoanStats] = useState(null);
    const [portfolioMetrics, setPortfolioMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [branches, setBranches] = useState([]);
    const [filters, setFilters] = useState({
        branch: '',
        loanType: '',
        status: ''
    });

    useEffect(() => {
        const fetchBranches = async () => {
            try {
                const response = await api.get(endpoints.branches);
                setBranches(response.data.results || response.data);
            } catch (error) {
                console.error("Error fetching branches:", error);
            }
        };
        fetchBranches();
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const params = {};
                if (filters.branch) params.branch = filters.branch;
                if (filters.loanType) params.loan_type = filters.loanType;
                if (filters.status) params.status = filters.status;

                const [loansRes, portfolioRes] = await Promise.all([
                    api.get(endpoints.stats.loans, { params }),
                    api.get(endpoints.stats.portfolio, { params })
                ]);
                setLoanStats(loansRes.data);
                setPortfolioMetrics(portfolioRes.data);
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [filters]);

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const clearFilters = () => {
        setFilters({ branch: '', loanType: '', status: '' });
    };

    if (loading) return <div className="flex items-center justify-center h-96">Loading analytics...</div>;

    // Format data for charts
    const loanTypeData = loanStats ? Object.entries(loanStats.by_loan_type).map(([name, value]) => ({ name, value })) : [];
    const branchData = loanStats ? Object.entries(loanStats.by_branch).map(([name, value]) => ({ name, value })) : [];

    const hasActiveFilters = filters.branch || filters.loanType || filters.status;

    return (
        <div className="space-y-6">
            {/* Header with Filters */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900">Portfolio Dashboard</h1>
                <div className="text-sm text-slate-500">
                    Last updated: {new Date().toLocaleDateString()}
                </div>
            </div>

            {/* Filters Bar */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                <div className="flex items-center gap-2 mb-3">
                    <Filter size={18} className="text-slate-600" />
                    <h3 className="font-semibold text-slate-700">Filters</h3>
                    {hasActiveFilters && (
                        <button
                            onClick={clearFilters}
                            className="ml-auto text-sm text-malawi-red hover:underline"
                        >
                            Clear All
                        </button>
                    )}
                </div>
                <div className="flex flex-wrap gap-4">
                    <select
                        className="px-4 py-2 border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-malawi-blue-500"
                        value={filters.branch}
                        onChange={(e) => handleFilterChange('branch', e.target.value)}
                    >
                        <option value="">All Branches</option>
                        {branches.map(branch => (
                            <option key={branch.id} value={branch.id}>{branch.name}</option>
                        ))}
                    </select>

                    <select
                        className="px-4 py-2 border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-malawi-blue-500"
                        value={filters.loanType}
                        onChange={(e) => handleFilterChange('loanType', e.target.value)}
                    >
                        <option value="">All Loan Types</option>
                        <option value="BUSINESS">Business Loan</option>
                        <option value="PAYDAY">PayDay Loan</option>
                        <option value="YOUTH">Youth Loan</option>
                        <option value="WOMEN">Women Loan</option>
                        <option value="MEN">Men Loan</option>
                    </select>

                    <select
                        className="px-4 py-2 border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-malawi-blue-500"
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                    >
                        <option value="">All Statuses</option>
                        <option value="ACTIVE">Active</option>
                        <option value="PENDING">Pending</option>
                        <option value="DEFAULTED">Defaulted</option>
                        <option value="CLOSED">Closed</option>
                    </select>
                </div>
            </div>

            {/* Key Metrics Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Portfolio"
                    value={`MWK ${Number(portfolioMetrics?.total_outstanding || 0).toLocaleString()}`}
                    subtext={`${loanStats?.total_loans} active loans`}
                    icon={Wallet}
                    color="bg-blue-600"
                />
                <StatCard
                    title="PAR 30 Days"
                    value={`${(Number(portfolioMetrics?.par30_rate || 0) * 100).toFixed(2)}%`}
                    subtext={`Risk: MWK ${Number(portfolioMetrics?.total_at_risk_30 || 0).toLocaleString()}`}
                    icon={AlertCircle}
                    color="bg-yellow-500"
                />
                <StatCard
                    title="Active Borrowers"
                    value={loanStats?.active_loans}
                    subtext="Across 9 branches"
                    icon={Users}
                    color="bg-malawi-green"
                />
                <StatCard
                    title="Avg Loan Size"
                    value={`MWK ${Number(loanStats?.avg_loan_amount || 0).toLocaleString()}`}
                    subtext="Per borrower"
                    icon={TrendingUp}
                    color="bg-purple-600"
                />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-semibold text-slate-800 mb-4">Loans by Type</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={loanTypeData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip formatter={(value) => [value, 'Loans']} />
                                <Bar dataKey="value" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-semibold text-slate-800 mb-4">Portfolio by Branch</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={branchData} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={100} />
                                <Tooltip formatter={(value) => [value, 'Loans']} />
                                <Bar dataKey="value" fill="#007A33" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Risk Analysis Section */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-slate-800">Risk Analysis (Bayesian Models)</h3>
                    <button className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800">
                        Retrain Models
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                        <h4 className="font-medium text-slate-700 mb-2">Probability of Default (PD)</h4>
                        <div className="text-3xl font-bold text-slate-900">
                            {(Number(portfolioMetrics?.pd_rate || 0) * 100).toFixed(1)}%
                        </div>
                        <p className="text-sm text-slate-500 mt-1">Mean posterior estimate</p>
                        <div className="mt-4 h-2 bg-slate-200 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-red-500 transition-all duration-500"
                                style={{ width: `${Math.min(Number(portfolioMetrics?.pd_rate || 0) * 100, 100)}%` }}
                            ></div>
                        </div>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                        <h4 className="font-medium text-slate-700 mb-2">Loss Given Default (LGD)</h4>
                        <div className="text-3xl font-bold text-slate-900">
                            {(Number(portfolioMetrics?.lgd_rate || 0) * 100).toFixed(1)}%
                        </div>
                        <p className="text-sm text-slate-500 mt-1">Beta distribution mean</p>
                        <div className="mt-4 h-2 bg-slate-200 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-orange-500 transition-all duration-500"
                                style={{ width: `${Math.min(Number(portfolioMetrics?.lgd_rate || 0) * 100, 100)}%` }}
                            ></div>
                        </div>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                        <h4 className="font-medium text-slate-700 mb-2">Portfolio VaR (95%)</h4>
                        <div className="text-3xl font-bold text-slate-900">
                            MWK {(Number(portfolioMetrics?.portfolio_var || 0) / 1000000).toFixed(1)}M
                        </div>
                        <p className="text-sm text-slate-500 mt-1">Value at Risk</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
