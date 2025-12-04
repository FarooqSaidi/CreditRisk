import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { endpoints } from '../services/api';
import { Search, MapPin, Briefcase, User, Phone } from 'lucide-react';

const BorrowerProfiles = () => {
    const [borrowers, setBorrowers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchBorrowers = async () => {
            setLoading(true);
            try {
                const response = await api.get(endpoints.borrowers);
                let data = response.data;

                // Client-side filtering
                if (searchTerm) {
                    const lower = searchTerm.toLowerCase();
                    data = data.filter(b =>
                        b.first_name.toLowerCase().includes(lower) ||
                        b.last_name.toLowerCase().includes(lower) ||
                        b.national_id.toLowerCase().includes(lower)
                    );
                }

                setBorrowers(data.results || data);
            } catch (error) {
                console.error("Error fetching borrowers:", error);
            } finally {
                setLoading(false);
            }
        };

        const timeoutId = setTimeout(() => fetchBorrowers(), 300);
        return () => clearTimeout(timeoutId);
    }, [searchTerm]);

    const handleViewProfile = (borrowerId) => {
        navigate(`/borrowers/${borrowerId}`);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900">Borrower Profiles</h1>
                <div className="relative w-72">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                    <input
                        type="text"
                        placeholder="Search borrowers..."
                        className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-malawi-blue-500"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3, 4, 5, 6].map(i => (
                        <div key={i} className="bg-white p-6 rounded-xl border border-slate-100 h-48 animate-pulse">
                            <div className="h-4 bg-slate-100 rounded w-1/2 mb-4"></div>
                            <div className="h-3 bg-slate-100 rounded w-3/4 mb-2"></div>
                            <div className="h-3 bg-slate-100 rounded w-1/2"></div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {borrowers.map((borrower) => (
                        <div key={borrower.id} className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow cursor-pointer group">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 font-bold text-lg group-hover:bg-malawi-red group-hover:text-white transition-colors">
                                        {borrower.first_name[0]}{borrower.last_name[0]}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-slate-900">{borrower.first_name} {borrower.last_name}</h3>
                                        <p className="text-xs text-slate-500">{borrower.national_id}</p>
                                    </div>
                                </div>
                                <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md font-medium">
                                    {borrower.loan_count} Loans
                                </span>
                            </div>

                            <div className="space-y-2 text-sm text-slate-600">
                                <div className="flex items-center gap-2">
                                    <MapPin size={16} className="text-slate-400" />
                                    <span>{borrower.traditional_authority}, {borrower.district}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Briefcase size={16} className="text-slate-400" />
                                    <span>{borrower.business_industry}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <User size={16} className="text-slate-400" />
                                    <span>{borrower.gender === 'M' ? 'Male' : 'Female'} • {new Date().getFullYear() - new Date(borrower.date_of_birth).getFullYear()} yrs</span>
                                </div>
                            </div>

                            <div className="mt-4 pt-4 border-t border-slate-50 flex justify-between items-center">
                                <div className="text-xs text-slate-500">
                                    Income: <span className="font-medium text-slate-900">MWK {Number(borrower.monthly_income).toLocaleString()}</span>
                                </div>
                                <button
                                    onClick={() => handleViewProfile(borrower.id)}
                                    className="text-sm text-malawi-red font-medium hover:underline"
                                >
                                    View Profile
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default BorrowerProfiles;
