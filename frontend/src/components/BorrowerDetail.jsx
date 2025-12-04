import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api, { endpoints } from '../services/api';
import { ArrowLeft, MapPin, Briefcase, User, Phone, Mail, Calendar, DollarSign, Shield } from 'lucide-react';

const BorrowerDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [borrower, setBorrower] = useState(null);
    const [loans, setLoans] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBorrowerDetails = async () => {
            if (!id) return;
            setLoading(true);
            try {
                // Fetch borrower first to ensure existence
                const borrowerRes = await api.get(`${endpoints.borrowers}${id}/`);
                setBorrower(borrowerRes.data);

                // Then fetch loans
                try {
                    const loansRes = await api.get(`${endpoints.borrowers}${id}/loans/`);
                    setLoans(loansRes.data);
                } catch (loanError) {
                    console.warn("Could not fetch loans for borrower", loanError);
                    setLoans([]);
                }
            } catch (error) {
                console.error("Error fetching borrower details:", error);
                setBorrower(null);
            } finally {
                setLoading(false);
            }
        };
        fetchBorrowerDetails();
    }, [id]);

    if (loading) {
        return <div className="flex items-center justify-center h-96">Loading borrower profile...</div>;
    }

    if (!borrower) {
        return <div className="text-center text-slate-500">Borrower not found</div>;
    }

    const age = new Date().getFullYear() - new Date(borrower.date_of_birth).getFullYear();
    const totalLoanAmount = loans.reduce((sum, loan) => sum + Number(loan.principal_amount), 0);
    const activeLoans = loans.filter(l => l.status === 'ACTIVE').length;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/borrowers')}
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">
                        {borrower.first_name} {borrower.last_name}
                    </h1>
                    <p className="text-sm text-slate-500">Borrower Profile</p>
                </div>
            </div>

            {/* Profile Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Personal Information */}
                <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h2 className="text-lg font-semibold text-slate-800 mb-4">Personal Information</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex items-start gap-3">
                            <User size={18} className="text-slate-400 mt-1" />
                            <div>
                                <p className="text-xs text-slate-500">National ID</p>
                                <p className="font-medium text-slate-900">{borrower.national_id}</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <Calendar size={18} className="text-slate-400 mt-1" />
                            <div>
                                <p className="text-xs text-slate-500">Age</p>
                                <p className="font-medium text-slate-900">{age} years ({borrower.gender === 'M' ? 'Male' : 'Female'})</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <Phone size={18} className="text-slate-400 mt-1" />
                            <div>
                                <p className="text-xs text-slate-500">Phone</p>
                                <p className="font-medium text-slate-900">{borrower.phone_number || 'N/A'}</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <MapPin size={18} className="text-slate-400 mt-1" />
                            <div>
                                <p className="text-xs text-slate-500">Location</p>
                                <p className="font-medium text-slate-900">{borrower.village}, {borrower.traditional_authority}</p>
                                <p className="text-xs text-slate-500">{borrower.district}</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <Briefcase size={18} className="text-slate-400 mt-1" />
                            <div>
                                <p className="text-xs text-slate-500">Business Industry</p>
                                <p className="font-medium text-slate-900">{borrower.business_industry}</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <DollarSign size={18} className="text-slate-400 mt-1" />
                            <div>
                                <p className="text-xs text-slate-500">Monthly Income</p>
                                <p className="font-medium text-slate-900">MWK {Number(borrower.monthly_income).toLocaleString()}</p>
                            </div>
                        </div>
                    </div>

                    {/* Spouse Information */}
                    {borrower.spouse && (
                        <div className="mt-6 pt-6 border-t border-slate-100">
                            <h3 className="font-semibold text-slate-700 mb-3">Spouse Information</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <p className="text-xs text-slate-500">Name</p>
                                    <p className="font-medium text-slate-900">{borrower.spouse.first_name} {borrower.spouse.last_name}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500">Employment Status</p>
                                    <p className="font-medium text-slate-900">{borrower.spouse.employment_status}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Guarantors */}
                    {borrower.guarantors && borrower.guarantors.length > 0 && (
                        <div className="mt-6 pt-6 border-t border-slate-100">
                            <h3 className="font-semibold text-slate-700 mb-3">Guarantors</h3>
                            <div className="space-y-3">
                                {borrower.guarantors.map((guarantor, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                                        <div>
                                            <p className="font-medium text-slate-900">{guarantor.first_name} {guarantor.last_name}</p>
                                            <p className="text-xs text-slate-500">{guarantor.relationship_to_borrower}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-xs text-slate-500">Phone</p>
                                            <p className="text-sm font-medium text-slate-900">{guarantor.phone_number}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Loan Summary */}
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                        <h2 className="text-lg font-semibold text-slate-800 mb-4">Loan Summary</h2>
                        <div className="space-y-4">
                            <div className="p-4 bg-blue-50 rounded-lg">
                                <p className="text-xs text-blue-600 mb-1">Total Loans</p>
                                <p className="text-2xl font-bold text-blue-900">{loans.length}</p>
                            </div>
                            <div className="p-4 bg-green-50 rounded-lg">
                                <p className="text-xs text-green-600 mb-1">Active Loans</p>
                                <p className="text-2xl font-bold text-green-900">{activeLoans}</p>
                            </div>
                            <div className="p-4 bg-purple-50 rounded-lg">
                                <p className="text-xs text-purple-600 mb-1">Total Borrowed</p>
                                <p className="text-xl font-bold text-purple-900">MWK {totalLoanAmount.toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Loan History */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <h2 className="text-lg font-semibold text-slate-800 mb-4">Loan History</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50 border-b border-slate-200">
                            <tr>
                                <th className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Loan #</th>
                                <th className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Type</th>
                                <th className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Amount</th>
                                <th className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Interest Rate</th>
                                <th className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Tenure</th>
                                <th className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                                <th className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Disbursed</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loans.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="px-4 py-8 text-center text-slate-500">No loans found</td>
                                </tr>
                            ) : (
                                loans.map((loan) => (
                                    <tr key={loan.id} className="hover:bg-slate-50">
                                        <td className="px-4 py-3 text-sm font-medium text-slate-900">{loan.loan_number}</td>
                                        <td className="px-4 py-3 text-sm text-slate-700 capitalize">{loan.loan_type.toLowerCase()}</td>
                                        <td className="px-4 py-3 text-sm font-medium text-slate-900">MWK {Number(loan.principal_amount).toLocaleString()}</td>
                                        <td className="px-4 py-3 text-sm text-slate-700">{(Number(loan.monthly_interest_rate) * 100).toFixed(1)}%</td>
                                        <td className="px-4 py-3 text-sm text-slate-700">{loan.tenure_months} months</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${loan.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                                                loan.status === 'DEFAULTED' ? 'bg-red-100 text-red-800' :
                                                    loan.status === 'CLOSED' ? 'bg-slate-100 text-slate-800' :
                                                        'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {loan.status}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-sm text-slate-500">
                                            {new Date(loan.disbursement_date).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default BorrowerDetail;
