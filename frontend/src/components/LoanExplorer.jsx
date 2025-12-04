import React, { useState, useEffect } from 'react';
import api, { endpoints } from '../services/api';
import { Search, Filter, ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import clsx from 'clsx';

const LoanExplorer = () => {
    const [loans, setLoans] = useState([]);
    const [branches, setBranches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        search: '',
        status: '',
        branch: '',
        loanType: ''
    });
    const [pagination, setPagination] = useState({
        page: 1,
        totalPages: 1,
        totalItems: 0
    });

    // Fetch branches
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

    // Fetch loans with filters
    useEffect(() => {
        const fetchLoans = async () => {
            setLoading(true);
            try {
                const params = {
                    page: pagination.page
                };

                // Add filters to params (only if they have values)
                if (filters.search) params.search = filters.search;
                if (filters.status) params.status = filters.status;
                if (filters.branch) params.branch = filters.branch;
                if (filters.loanType) params.loan_type = filters.loanType;

                const response = await api.get(endpoints.loans, { params });

                // Handle both paginated and non-paginated responses
                if (response.data.results) {
                    // Paginated response
                    setLoans(response.data.results);
                    setPagination(prev => ({
                        ...prev,
                        totalItems: response.data.count,
                        totalPages: Math.ceil(response.data.count / 50)
                    }));
                } else if (Array.isArray(response.data)) {
                    // Non-paginated array response
                    setLoans(response.data);
                    setPagination(prev => ({ ...prev, totalItems: response.data.length }));
                }
            } catch (error) {
                console.error("Error fetching loans:", error);
            } finally {
                setLoading(false);
            }
        };

        // Debounce search
        const timeoutId = setTimeout(() => fetchLoans(), 300);
        return () => clearTimeout(timeoutId);
    }, [filters, pagination.page]);

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
        setPagination(prev => ({ ...prev, page: 1 })); // Reset to page 1
    };

    const clearFilters = () => {
        setFilters({ search: '', status: '', branch: '', loanType: '' });
    };

    const hasActiveFilters = filters.search || filters.status || filters.branch || filters.loanType;

    const StatusBadge = ({ status }) => {
        const styles = {
            ACTIVE: "bg-green-100 text-green-800",
            PENDING: "bg-yellow-100 text-yellow-800",
            DEFAULTED: "bg-red-100 text-red-800",
            CLOSED: "bg-slate-100 text-slate-800",
            WRITTEN_OFF: "bg-gray-800 text-white"
        };
        return (
            <span className={clsx("px-2 py-1 rounded-full text-xs font-medium", styles[status] || "bg-gray-100")}>
                {status}
            </span>
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900">Loan Explorer</h1>
                <button className="bg-malawi-red text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                    New Loan Application
                </button>
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
                <div className="flex flex-wrap gap-4 items-center">
                    <div className="flex-1 min-w-[200px] relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                        <input
                            type="text"
                            placeholder="Search by loan # or borrower..."
                            className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-malawi-blue-500"
                            value={filters.search}
                            onChange={(e) => handleFilterChange('search', e.target.value)}
                        />
                    </div>

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
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                    >
                        <option value="">All Statuses</option>
                        <option value="ACTIVE">Active</option>
                        <option value="PENDING">Pending</option>
                        <option value="DEFAULTED">Defaulted</option>
                        <option value="CLOSED">Closed</option>
                    </select>

                    <select
                        className="px-4 py-2 border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-malawi-blue-500"
                        value={filters.loanType}
                        onChange={(e) => handleFilterChange('loanType', e.target.value)}
                    >
                        <option value="">All Types</option>
                        <option value="BUSINESS">Business</option>
                        <option value="PAYDAY">PayDay</option>
                        <option value="YOUTH">Youth</option>
                        <option value="WOMEN">Women</option>
                        <option value="MEN">Men</option>
                    </select>
                </div>
            </div>

            {/* Data Table */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50 border-b border-slate-200">
                            <tr>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Loan #</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Borrower</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Branch</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Amount (MWK)</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Type</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loading ? (
                                <tr>
                                    <td colSpan="7" className="px-6 py-8 text-center text-slate-500">Loading loan data...</td>
                                </tr>
                            ) : loans.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="px-6 py-8 text-center text-slate-500">No loans found matching your filters.</td>
                                </tr>
                            ) : (
                                loans.map((loan) => (
                                    <tr key={loan.id} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 text-sm font-medium text-slate-900">{loan.loan_number}</td>
                                        <td className="px-6 py-4 text-sm text-slate-700">{loan.borrower_name}</td>
                                        <td className="px-6 py-4 text-sm text-slate-500">{loan.branch_name}</td>
                                        <td className="px-6 py-4 text-sm font-medium text-slate-900">
                                            {Number(loan.principal_amount).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-slate-500 capitalize">{loan.loan_type.toLowerCase()}</td>
                                        <td className="px-6 py-4">
                                            <StatusBadge status={loan.status} />
                                        </td>
                                        <td className="px-6 py-4">
                                            <button className="text-slate-400 hover:text-malawi-blue-600 transition-colors">
                                                <Eye size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
                    <p className="text-sm text-slate-500">
                        Showing <span className="font-medium">{loans.length}</span> of <span className="font-medium">{pagination.totalItems}</span> results
                    </p>
                    <div className="flex gap-2">
                        <button
                            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50"
                            disabled={pagination.page === 1}
                            onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                        >
                            <ChevronLeft size={16} />
                        </button>
                        <div className="px-4 py-2 text-sm text-slate-700">
                            Page {pagination.page} of {pagination.totalPages || 1}
                        </div>
                        <button
                            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50"
                            disabled={pagination.page >= pagination.totalPages}
                            onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                        >
                            <ChevronRight size={16} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoanExplorer;
