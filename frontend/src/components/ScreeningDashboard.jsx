import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield, TrendingUp, AlertTriangle, CheckCircle, XCircle, DollarSign,
    ChevronDown, ChevronUp, FileText, Users, Briefcase, Home, CreditCard
} from 'lucide-react';
import {
    PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend
} from 'recharts';

const ScreeningDashboard = ({ result, onReset }) => {
    const [expandedSection, setExpandedSection] = useState(null);

    if (!result) return null;

    const {
        cluster_group, client_risk_score, recommended_loan_amount, requested_amount,
        id
    } = result;

    // Mock detailed data (since backend currently returns limited mock data)
    // In a real scenario, these would come from the API response
    const detailedMetrics = {
        collateral_coverage: 120, // %
        debt_to_income: 35, // %
        business_stability: 80, // Score
        social_capital: 75, // Score
        character_score: 90, // Score
        monthly_income: 450000,
        monthly_expenses: 280000,
        monthly_loan_payment: 50000, // Estimated
    };

    const radarData = [
        { subject: 'Collateral', A: detailedMetrics.collateral_coverage > 100 ? 100 : detailedMetrics.collateral_coverage, fullMark: 100 },
        { subject: 'Cashflow', A: 100 - detailedMetrics.debt_to_income, fullMark: 100 },
        { subject: 'Character', A: detailedMetrics.character_score, fullMark: 100 },
        { subject: 'Business', A: detailedMetrics.business_stability, fullMark: 100 },
        { subject: 'Social', A: detailedMetrics.social_capital, fullMark: 100 },
    ];

    const financialData = [
        { name: 'Income', amount: detailedMetrics.monthly_income },
        { name: 'Expenses', amount: detailedMetrics.monthly_expenses },
        { name: 'Loan Pmt', amount: detailedMetrics.monthly_loan_payment },
    ];

    const getRiskColor = (cluster) => {
        switch (cluster) {
            case 'LOW': return 'text-green-600 bg-green-100 border-green-200';
            case 'MEDIUM': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
            case 'HIGH': return 'text-red-600 bg-red-100 border-red-200';
            default: return 'text-gray-600 bg-gray-100 border-gray-200';
        }
    };

    const toggleSection = (section) => {
        setExpandedSection(expandedSection === section ? null : section);
    };

    return (
        <div className="bg-gray-50 min-h-screen p-8">
            <div className="max-w-6xl mx-auto space-y-8">

                {/* Header Section */}
                <div className="bg-white rounded-2xl shadow-sm p-8 border border-gray-100">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="flex items-center gap-4">
                            <div className="p-4 rounded-full bg-blue-50">
                                <Shield className="w-10 h-10 text-blue-600" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-gray-900">Screening Report #{id}</h1>
                                <p className="text-gray-500">Generated on {new Date().toLocaleDateString()}</p>
                            </div>
                        </div>
                        <div className={`px-6 py-3 rounded-full border-2 font-bold text-xl flex items-center gap-2 ${getRiskColor(cluster_group)}`}>
                            <AlertTriangle className="w-6 h-6" />
                            {cluster_group} RISK PROFILE
                        </div>
                    </div>
                </div>

                {/* Main Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                    {/* Score Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        className="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                    >
                        <h3 className="text-gray-500 font-medium mb-4 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4" /> Overall Score
                        </h3>
                        <div className="flex items-center justify-center h-48">
                            <div className="relative w-40 h-40 flex items-center justify-center">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={[{ value: client_risk_score }, { value: 100 - client_risk_score }]}
                                            innerRadius={60}
                                            outerRadius={80}
                                            startAngle={180}
                                            endAngle={0}
                                            dataKey="value"
                                        >
                                            <Cell fill={client_risk_score > 70 ? '#10B981' : client_risk_score > 40 ? '#F59E0B' : '#EF4444'} />
                                            <Cell fill="#E5E7EB" />
                                        </Pie>
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="absolute text-center">
                                    <span className="text-4xl font-bold text-gray-900">{client_risk_score}</span>
                                    <p className="text-xs text-gray-400">/100</p>
                                </div>
                            </div>
                        </div>
                        <p className="text-center text-sm text-gray-500 mt-2">
                            Higher score indicates lower probability of default.
                        </p>
                    </motion.div>

                    {/* Radar Chart */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                        className="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                    >
                        <h3 className="text-gray-500 font-medium mb-4 flex items-center gap-2">
                            <Shield className="w-4 h-4" /> Risk Dimensions (5 Cs)
                        </h3>
                        <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                                    <PolarGrid />
                                    <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10 }} />
                                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                                    <Radar name="Client" dataKey="A" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
                                    <Tooltip />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    </motion.div>

                    {/* Loan Recommendation */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                        className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between"
                    >
                        <div>
                            <h3 className="text-gray-500 font-medium mb-4 flex items-center gap-2">
                                <DollarSign className="w-4 h-4" /> Recommendation
                            </h3>
                            <div className="mb-6">
                                <p className="text-sm text-gray-400 mb-1">Requested</p>
                                <p className="text-xl font-semibold text-gray-600">MWK {parseFloat(requested_amount).toLocaleString()}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-400 mb-1">Approved Limit</p>
                                <p className="text-3xl font-bold text-blue-600">MWK {parseFloat(recommended_loan_amount).toLocaleString()}</p>
                            </div>
                        </div>
                        <div className="mt-4 pt-4 border-t border-gray-100">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500">Approval Rate</span>
                                <span className="font-medium text-gray-900">
                                    {Math.round((recommended_loan_amount / requested_amount) * 100)}%
                                </span>
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Financial Analysis */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                    className="bg-white p-8 rounded-xl shadow-sm border border-gray-100"
                >
                    <h3 className="text-xl font-bold text-gray-800 mb-6">Financial Capacity Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={financialData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                    <XAxis type="number" hide />
                                    <YAxis dataKey="name" type="category" width={80} />
                                    <Tooltip formatter={(value) => `MWK ${value.toLocaleString()}`} />
                                    <Bar dataKey="amount" fill="#3B82F6" radius={[0, 4, 4, 0]}>
                                        {financialData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={index === 0 ? '#10B981' : index === 1 ? '#EF4444' : '#F59E0B'} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="space-y-4">
                            <div className="p-4 bg-gray-50 rounded-lg">
                                <div className="flex justify-between mb-2">
                                    <span className="text-gray-600">Net Monthly Cashflow</span>
                                    <span className="font-bold text-green-600">MWK {(detailedMetrics.monthly_income - detailedMetrics.monthly_expenses).toLocaleString()}</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                                </div>
                            </div>
                            <div className="p-4 bg-gray-50 rounded-lg">
                                <div className="flex justify-between mb-2">
                                    <span className="text-gray-600">Debt-to-Income Ratio</span>
                                    <span className={`font-bold ${detailedMetrics.debt_to_income > 40 ? 'text-red-600' : 'text-blue-600'}`}>
                                        {detailedMetrics.debt_to_income}%
                                    </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div className={`h-2 rounded-full ${detailedMetrics.debt_to_income > 40 ? 'bg-red-500' : 'bg-blue-500'}`} style={{ width: `${detailedMetrics.debt_to_income}%` }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Collapsible Input Summary */}
                <div className="space-y-4">
                    <h3 className="text-xl font-bold text-gray-800">Screening Data Summary</h3>

                    {/* Business Section */}
                    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                        <button
                            onClick={() => toggleSection('business')}
                            className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <Briefcase className="w-5 h-5 text-gray-500" />
                                <span className="font-medium text-gray-700">Business Assessment</span>
                            </div>
                            {expandedSection === 'business' ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
                        </button>
                        <AnimatePresence>
                            {expandedSection === 'business' && (
                                <motion.div
                                    initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
                                    className="overflow-hidden"
                                >
                                    <div className="p-6 border-t border-gray-100">
                                        <p className="text-gray-500 italic">Detailed business data would appear here...</p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Household Section */}
                    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                        <button
                            onClick={() => toggleSection('household')}
                            className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <Home className="w-5 h-5 text-gray-500" />
                                <span className="font-medium text-gray-700">Household & Assets</span>
                            </div>
                            {expandedSection === 'household' ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
                        </button>
                        <AnimatePresence>
                            {expandedSection === 'household' && (
                                <motion.div
                                    initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
                                    className="overflow-hidden"
                                >
                                    <div className="p-6 border-t border-gray-100">
                                        <p className="text-gray-500 italic">Detailed household data would appear here...</p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Social/Trust Section */}
                    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                        <button
                            onClick={() => toggleSection('social')}
                            className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <Users className="w-5 h-5 text-gray-500" />
                                <span className="font-medium text-gray-700">Social Capital & Trust</span>
                            </div>
                            {expandedSection === 'social' ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
                        </button>
                        <AnimatePresence>
                            {expandedSection === 'social' && (
                                <motion.div
                                    initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
                                    className="overflow-hidden"
                                >
                                    <div className="p-6 border-t border-gray-100">
                                        <p className="text-gray-500 italic">Detailed trust game results would appear here...</p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-center gap-4 pt-8 pb-12">
                    <button onClick={onReset} className="px-8 py-3 bg-white border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 font-medium shadow-sm transition-all">
                        Start New Screening
                    </button>
                    <button className="px-8 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-medium shadow-lg flex items-center gap-2 transition-all transform hover:scale-105">
                        <FileText className="w-5 h-5" /> Download Full Report
                    </button>
                    <button className="px-8 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 font-medium shadow-lg flex items-center gap-2 transition-all transform hover:scale-105">
                        <CheckCircle className="w-5 h-5" /> Approve Loan
                    </button>
                </div>

            </div>
        </div>
    );
};

export default ScreeningDashboard;
