import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    User, Home, Briefcase, Users, DollarSign, CheckCircle,
    AlertTriangle, Plus, Trash2, Camera, MapPin, FileText,
    CreditCard, Shield, Activity
} from 'lucide-react';
import api from '../services/api';
import TrustGameWidget from './TrustGameWidget';

const ClientScreeningForm = ({ borrowerId, onComplete }) => {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [screeningId, setScreeningId] = useState(null);

    // Form State
    const [formData, setFormData] = useState({
        // Step 1: Client Info
        borrower: borrowerId,
        loan_usage_intention: '',
        requested_amount: '',
        past_defaults: false,
        education_level: 'PRIMARY',
        residence_type: 'OWNED',
        id_type: 'NATIONAL_ID',

        // Step 2: Informal Loans (Array)
        informal_loans: [],

        // Step 3: Identity & Behavioral
        id_photo: null,
        client_photo: null,
        answered_by_proxy: false,

        // Step 4: Spouse (Conditional)
        marital_status: 'SINGLE',
        spouse_support_score: 50,
        spouse_trust_score: 50,
        spouse_supports_loan: true,
        spouse_aware_of_debts: true,

        // Step 5: Guarantors (Array)
        guarantors: [],

        // Step 6: Client Collaterals (Array)
        client_collaterals: [],

        // Step 7: Household
        months_at_residence: '',
        number_of_dependents: '',
        total_monthly_income: '',
        total_monthly_expenses: '',
        liquid_assets: '',

        // Step 8: Businesses (Array)
        businesses: []
    });

    // Helper to update simple fields
    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    // Helper for dynamic arrays (loans, guarantors, businesses)
    const addItem = (field, initialItem) => {
        setFormData(prev => ({
            ...prev,
            [field]: [...prev[field], initialItem]
        }));
    };

    const removeItem = (field, index) => {
        setFormData(prev => ({
            ...prev,
            [field]: prev[field].filter((_, i) => i !== index)
        }));
    };

    const updateItem = (field, index, subField, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: prev[field].map((item, i) =>
                i === index ? { ...item, [subField]: value } : item
            )
        }));
    };

    // --- API SUBMISSION ---
    const submitScreening = async () => {
        setLoading(true);
        try {
            // 1. Create Base Screening
            const screeningRes = await api.post('/client-screenings/', {
                borrower: formData.borrower,
                loan_usage_intention: formData.loan_usage_intention,
                requested_amount: formData.requested_amount,
                past_defaults: formData.past_defaults,
                status: 'DRAFT'
            });
            const newId = screeningRes.data.id;
            setScreeningId(newId);

            // 2. Client Profile
            await api.post('/client-profiles/', {
                screening: newId,
                education_level: formData.education_level,
                residence_type: formData.residence_type,
                id_type: formData.id_type,
                months_at_residence: formData.months_at_residence || 0,
                number_of_dependents: formData.number_of_dependents || 0,
                number_of_active_businesses: formData.businesses.length || 1,
                id_number: "N/A" // Mocking ID number as it's not in the form
            });

            // 3. Informal Loans
            for (const loan of formData.informal_loans) {
                await api.post('/informal-loans/', {
                    screening: newId,
                    ...loan,
                    repayment_schedule: "MONTHLY" // Default
                });
            }

            // 4. Spouse Assessment (if married)
            if (formData.marital_status === 'MARRIED') {
                await api.post('/spouse-assessments/', {
                    screening: newId,
                    supports_loan: formData.spouse_supports_loan,
                    aware_of_debts: formData.spouse_aware_of_debts,
                    cooperation_score: formData.spouse_support_score, // Mapping UI score to model
                    full_name: "Spouse Name", // Placeholder as it's not in the form
                    financial_involvement: "MEDIUM", // Default
                    decision_making_power: "PARTIAL", // Default
                    q_support_repayment: 4, // Default (Max)
                    q_intervene_if_missed: 3 // Default (Max)
                });
            }

            // 5. Guarantors
            for (const g of formData.guarantors) {
                const gRes = await api.post('/guarantor-assessments/', {
                    screening: newId,
                    full_name: g.full_name,
                    relationship_to_client: g.relationship,
                    voluntary_guarantor: g.voluntary,
                    has_past_defaults: g.defaults,
                    trust_score: g.trust_score,
                    monthly_income: 0, // Default
                    liquid_assets: 0, // Default
                    q_willingness_to_repay: 4, // Default (Max)
                    q_aware_of_debts: true, // Default
                    q_incentive_alignment: 2, // Default (Max)
                    q_past_reliability: 2 // Default (Max)
                });
                // Add Guarantor Collateral if any
                if (g.collateral_type) {
                    await api.post('/guarantor-collaterals/', {
                        guarantor: gRes.data.id,
                        collateral_type: g.collateral_type,
                        estimated_value: g.collateral_value,
                        physical_condition: 'GOOD', // Default
                        ownership_verified: true,
                        description: "N/A", // Default
                        seizure_difficulty: "LOW", // Default
                        collateral_name: "Guarantor Collateral" // Default
                    });
                }
            }

            // 6. Client Collaterals
            for (const c of formData.client_collaterals) {
                await api.post('/client-collaterals/', {
                    screening: newId,
                    collateral_type: c.type,
                    estimated_value: c.value,
                    physical_condition: c.condition,
                    ownership_verified: true,
                    description: "N/A", // Default
                    seizure_difficulty: "LOW", // Default
                    collateral_name: "Client Collateral" // Default
                });
            }

            // 7. Household Assessment
            // Auto-calculate net cashflow
            const netCashflow = parseFloat(formData.total_monthly_income || 0) - parseFloat(formData.total_monthly_expenses || 0);
            await api.post('/household-assessments/', {
                screening: newId,
                months_at_residence: formData.months_at_residence,
                number_of_dependents: formData.number_of_dependents,
                total_monthly_income: formData.total_monthly_income,
                total_monthly_expenses: formData.total_monthly_expenses,
                net_monthly_cashflow: netCashflow,
                liquid_assets: formData.liquid_assets,
                household_stability_years: (formData.months_at_residence / 12).toFixed(1) // Calculated
            });

            // 8. Business Assessments
            for (const b of formData.businesses) {
                const profit = parseFloat(b.revenue || 0) - parseFloat(b.costs || 0);
                const bRes = await api.post('/business-assessments/', {
                    screening: newId,
                    business_name: b.name,
                    business_type: b.type,
                    business_age_years: b.age,
                    monthly_revenue: b.revenue,
                    monthly_costs: b.costs,
                    monthly_profit: profit,
                    number_of_employees: b.employees,
                    number_of_outlets: 1, // Default
                    seasonality_index: 50, // Default
                    monthly_salaries: 0, // Default
                    monthly_rent: 0, // Default
                    monthly_utilities: 0, // Default
                    daily_selling_tax: 0, // Default
                    daily_transport_home_to_shop: 0, // Default
                    monthly_transport_to_supplier: 0, // Default
                    daily_food_at_shop: 0, // Default
                    monthly_food_supplier_trips: 0 // Default
                });

                // Add Items
                if (b.top_item) {
                    await api.post('/business-items/', {
                        business: bRes.data.id,
                        item_name: b.top_item,
                        purchase_price: 0, // Simplified
                        selling_price: 0,
                        margin_percentage: 0,
                        quantity_sold_per_month: 0, // Default
                        selling_price_per_unit: 0, // Default
                        buying_price_per_unit: 0, // Default
                        current_stock_quantity: 0 // Default
                    });
                }
            }

            // 9. Behavioral Verification
            await api.post('/behavioral-verifications/', {
                screening: newId,
                answered_by_proxy: formData.answered_by_proxy,
                nervousness_score: 1, // Default
                inconsistent_answers: false,
                daily_cashflow_answer: "N/A", // Default
                key_suppliers_answer: "N/A", // Default
                key_clients_answer: "N/A", // Default
                business_routine_answer: "N/A" // Default
            });

            // Final: Calculate Risk
            const resultRes = await api.post(`/client-screenings/${newId}/calculate_risk/`);

            if (onComplete) onComplete(resultRes.data);

            if (onComplete) onComplete(resultRes.data);

        } catch (error) {
            console.error("Submission failed", error);
            console.error("Error response:", error.response?.data);
            
            let errorMessage = "Unknown error";
            if (error.response?.data) {
                // Handle Django REST Framework validation errors
                if (typeof error.response.data === 'object') {
                    errorMessage = JSON.stringify(error.response.data, null, 2);
                } else {
                    errorMessage = error.response.data.detail || error.response.data;
                }
            } else {
                errorMessage = error.message;
            }
            
            alert(`Failed to submit screening. Error: ${errorMessage}. Please check console for details.`);
        } finally {
            setLoading(false);
        }
    };

    // --- RENDER STEPS ---

    const renderStep1_ClientInfo = () => (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <User className="w-6 h-6 text-blue-600" /> Client Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Loan Usage Intention</label>
                    <textarea name="loan_usage_intention" value={formData.loan_usage_intention} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2" rows="3" placeholder="Describe usage..." />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Requested Amount (MWK)</label>
                    <input type="number" name="requested_amount" value={formData.requested_amount} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Education Level</label>
                    <select name="education_level" value={formData.education_level} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 border p-2">
                        <option value="NONE">None</option>
                        <option value="PRIMARY">Primary</option>
                        <option value="SECONDARY">Secondary</option>
                        <option value="TERTIARY">Tertiary</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Marital Status</label>
                    <select name="marital_status" value={formData.marital_status} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 border p-2">
                        <option value="SINGLE">Single</option>
                        <option value="MARRIED">Married</option>
                        <option value="DIVORCED">Divorced</option>
                        <option value="WIDOWED">Widowed</option>
                    </select>
                </div>
                <div className="flex items-center pt-6">
                    <input type="checkbox" name="past_defaults" checked={formData.past_defaults} onChange={handleChange} className="h-4 w-4 text-blue-600 rounded" />
                    <label className="ml-2 block text-sm text-gray-900">Has Past Defaults?</label>
                </div>
            </div>
        </div>
    );

    const renderStep2_InformalLoans = () => (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <CreditCard className="w-6 h-6 text-orange-600" /> Informal Loans
            </h3>
            <p className="text-sm text-gray-500">Add any existing informal debts (Katapila, family, friends).</p>

            {formData.informal_loans.map((loan, idx) => (
                <div key={idx} className="bg-gray-50 p-4 rounded-lg border relative">
                    <button onClick={() => removeItem('informal_loans', idx)} className="absolute top-2 right-2 text-red-500 hover:text-red-700"><Trash2 className="w-4 h-4" /></button>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <input type="text" placeholder="Lender Name" value={loan.lender_name} onChange={(e) => updateItem('informal_loans', idx, 'lender_name', e.target.value)} className="rounded border p-2" />
                        <input type="number" placeholder="Amount (MWK)" value={loan.amount} onChange={(e) => updateItem('informal_loans', idx, 'amount', e.target.value)} className="rounded border p-2" />
                        <select value={loan.lender_relationship} onChange={(e) => updateItem('informal_loans', idx, 'lender_relationship', e.target.value)} className="rounded border p-2">
                            <option value="MONEYLENDER">Moneylender (Katapila)</option>
                            <option value="FAMILY">Family</option>
                            <option value="FRIEND">Friend</option>
                        </select>
                    </div>
                </div>
            ))}

            <button onClick={() => addItem('informal_loans', { lender_name: '', amount: '', lender_relationship: 'MONEYLENDER' })} className="flex items-center text-blue-600 hover:text-blue-800 font-medium">
                <Plus className="w-4 h-4 mr-1" /> Add Informal Loan
            </button>
        </div>
    );

    const renderStep3_Identity = () => (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <Shield className="w-6 h-6 text-purple-600" /> Identity & Behavior
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 cursor-pointer relative">
                    <input
                        type="file"
                        accept="image/*"
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        onChange={(e) => setFormData(prev => ({ ...prev, id_photo: e.target.files[0] }))}
                    />
                    {formData.id_photo ? (
                        <div className="flex flex-col items-center">
                            <CheckCircle className="w-8 h-8 text-green-500 mb-2" />
                            <span className="text-sm font-medium text-gray-900">{formData.id_photo.name}</span>
                            <span className="text-xs text-gray-500">Click to change</span>
                        </div>
                    ) : (
                        <>
                            <Camera className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                            <span className="text-sm text-gray-500">Upload ID Photo</span>
                        </>
                    )}
                </div>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 cursor-pointer relative">
                    <input
                        type="file"
                        accept="image/*"
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        onChange={(e) => setFormData(prev => ({ ...prev, client_photo: e.target.files[0] }))}
                    />
                    {formData.client_photo ? (
                        <div className="flex flex-col items-center">
                            <CheckCircle className="w-8 h-8 text-green-500 mb-2" />
                            <span className="text-sm font-medium text-gray-900">{formData.client_photo.name}</span>
                            <span className="text-xs text-gray-500">Click to change</span>
                        </div>
                    ) : (
                        <>
                            <User className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                            <span className="text-sm text-gray-500">Upload Client Photo</span>
                        </>
                    )}
                </div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <label className="flex items-center">
                    <input type="checkbox" name="answered_by_proxy" checked={formData.answered_by_proxy} onChange={handleChange} className="h-4 w-4 text-yellow-600 rounded" />
                    <span className="ml-2 text-sm text-gray-900 font-medium">Is someone else answering for the client? (Proxy)</span>
                </label>
            </div>
        </div>
    );

    const renderStep4_Spouse = () => {
        if (formData.marital_status !== 'MARRIED') {
            return (
                <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
                    <div className="bg-gray-100 p-4 rounded-full">
                        <Users className="w-8 h-8 text-gray-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-medium text-gray-900">Spouse Assessment Skipped</h3>
                        <p className="text-gray-500 max-w-sm mx-auto mt-1">
                            This step is not applicable because the client's marital status is set to <strong>{formData.marital_status.toLowerCase()}</strong>.
                        </p>
                    </div>
                    <button
                        onClick={() => setStep(5)}
                        className="mt-4 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 font-medium text-sm"
                    >
                        Continue to Next Step
                    </button>
                </div>
            );
        }
        return (
            <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                    <Users className="w-6 h-6 text-pink-600" /> Spouse Assessment
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex items-center">
                        <input type="checkbox" name="spouse_supports_loan" checked={formData.spouse_supports_loan} onChange={handleChange} className="h-4 w-4 text-blue-600 rounded" />
                        <label className="ml-2 block text-sm text-gray-900">Spouse supports this loan?</label>
                    </div>
                    <div className="flex items-center">
                        <input type="checkbox" name="spouse_aware_of_debts" checked={formData.spouse_aware_of_debts} onChange={handleChange} className="h-4 w-4 text-blue-600 rounded" />
                        <label className="ml-2 block text-sm text-gray-900">Spouse aware of other debts?</label>
                    </div>
                </div>

                <TrustGameWidget
                    type="SPOUSE"
                    onComplete={(score) => setFormData(prev => ({ ...prev, spouse_support_score: score }))}
                />
            </div>
        );
    };

    const renderStep5_Guarantors = () => (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <Users className="w-6 h-6 text-green-600" /> Guarantors
            </h3>
            {formData.guarantors.map((g, idx) => (
                <div key={idx} className="bg-gray-50 p-4 rounded-lg border relative space-y-3">
                    <button onClick={() => removeItem('guarantors', idx)} className="absolute top-2 right-2 text-red-500 hover:text-red-700"><Trash2 className="w-4 h-4" /></button>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input type="text" placeholder="Full Name" value={g.full_name} onChange={(e) => updateItem('guarantors', idx, 'full_name', e.target.value)} className="rounded border p-2" />
                        <input type="text" placeholder="Relationship" value={g.relationship} onChange={(e) => updateItem('guarantors', idx, 'relationship', e.target.value)} className="rounded border p-2" />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <label className="flex items-center"><input type="checkbox" checked={g.voluntary} onChange={(e) => updateItem('guarantors', idx, 'voluntary', e.target.checked)} className="mr-2" /> Voluntary?</label>
                        <label className="flex items-center"><input type="checkbox" checked={g.defaults} onChange={(e) => updateItem('guarantors', idx, 'defaults', e.target.checked)} className="mr-2" /> Past Defaults?</label>
                    </div>

                    <div className="mt-4">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Guarantor Trust Assessment</h4>
                        <TrustGameWidget
                            type="GUARANTOR"
                            onComplete={(score) => updateItem('guarantors', idx, 'trust_score', score)}
                        />
                    </div>
                </div>
            ))}
            <button onClick={() => addItem('guarantors', { full_name: '', relationship: '', voluntary: true, defaults: false, trust_score: 50, collateral_type: '', collateral_value: '' })} className="flex items-center text-blue-600 font-medium">
                <Plus className="w-4 h-4 mr-1" /> Add Guarantor
            </button>
        </div>
    );

    const renderStep6_Collaterals = () => (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <Home className="w-6 h-6 text-indigo-600" /> Client Collateral
            </h3>
            {formData.client_collaterals.map((c, idx) => (
                <div key={idx} className="bg-gray-50 p-4 rounded-lg border relative grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button onClick={() => removeItem('client_collaterals', idx)} className="absolute top-2 right-2 text-red-500 hover:text-red-700"><Trash2 className="w-4 h-4" /></button>
                    <select value={c.type} onChange={(e) => updateItem('client_collaterals', idx, 'type', e.target.value)} className="rounded border p-2">
                        <option value="HOUSEHOLD_ITEM">Household Item</option>
                        <option value="LIVESTOCK">Livestock</option>
                        <option value="VEHICLE">Vehicle</option>
                        <option value="LAND">Land</option>
                    </select>
                    <input type="number" placeholder="Value (MWK)" value={c.value} onChange={(e) => updateItem('client_collaterals', idx, 'value', e.target.value)} className="rounded border p-2" />
                    <select value={c.condition} onChange={(e) => updateItem('client_collaterals', idx, 'condition', e.target.value)} className="rounded border p-2">
                        <option value="NEW">New</option>
                        <option value="GOOD">Good</option>
                        <option value="FAIR">Fair</option>
                        <option value="POOR">Poor</option>
                    </select>
                </div>
            ))}
            <button onClick={() => addItem('client_collaterals', { type: 'HOUSEHOLD_ITEM', value: '', condition: 'GOOD' })} className="flex items-center text-blue-600 font-medium">
                <Plus className="w-4 h-4 mr-1" /> Add Collateral
            </button>
        </div>
    );

    const renderStep7_Household = () => (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <Home className="w-6 h-6 text-teal-600" /> Household Assessment
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Total Monthly Income</label>
                    <input type="number" name="total_monthly_income" value={formData.total_monthly_income} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Total Monthly Expenses</label>
                    <input type="number" name="total_monthly_expenses" value={formData.total_monthly_expenses} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Dependents</label>
                    <input type="number" name="number_of_dependents" value={formData.number_of_dependents} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Liquid Assets</label>
                    <input type="number" name="liquid_assets" value={formData.liquid_assets} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
                </div>
            </div>
        </div>
    );

    const renderStep8_Business = () => (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <Briefcase className="w-6 h-6 text-blue-800" /> Business Assessment
            </h3>
            {formData.businesses.map((b, idx) => (
                <div key={idx} className="bg-gray-50 p-4 rounded-lg border relative space-y-4">
                    <button onClick={() => removeItem('businesses', idx)} className="absolute top-2 right-2 text-red-500 hover:text-red-700"><Trash2 className="w-4 h-4" /></button>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input type="text" placeholder="Business Name" value={b.name} onChange={(e) => updateItem('businesses', idx, 'name', e.target.value)} className="rounded border p-2" />
                        <select value={b.type} onChange={(e) => updateItem('businesses', idx, 'type', e.target.value)} className="rounded border p-2">
                            <option value="RETAIL">Retail</option>
                            <option value="SERVICE">Service</option>
                            <option value="AGRICULTURE">Agriculture</option>
                            <option value="MANUFACTURING">Manufacturing</option>
                        </select>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <input type="number" placeholder="Monthly Revenue" value={b.revenue} onChange={(e) => updateItem('businesses', idx, 'revenue', e.target.value)} className="rounded border p-2" />
                        <input type="number" placeholder="Monthly Costs" value={b.costs} onChange={(e) => updateItem('businesses', idx, 'costs', e.target.value)} className="rounded border p-2" />
                        <input type="number" placeholder="Employees" value={b.employees} onChange={(e) => updateItem('businesses', idx, 'employees', e.target.value)} className="rounded border p-2" />
                    </div>
                    <input type="text" placeholder="Top Selling Item" value={b.top_item} onChange={(e) => updateItem('businesses', idx, 'top_item', e.target.value)} className="w-full rounded border p-2" />
                </div>
            ))}
            <button onClick={() => addItem('businesses', { name: '', type: 'RETAIL', revenue: '', costs: '', employees: '', top_item: '', age: '' })} className="flex items-center text-blue-600 font-medium">
                <Plus className="w-4 h-4 mr-1" /> Add Business
            </button>
        </div>
    );

    const renderStep9_Review = () => (
        <div className="space-y-6 text-center">
            <h3 className="text-2xl font-bold text-gray-800">Review & Submit</h3>
            <p className="text-gray-600">Please review all information before submitting for risk analysis.</p>

            <div className="bg-blue-50 p-6 rounded-lg text-left space-y-2">
                <p><strong>Amount:</strong> MWK {formData.requested_amount}</p>
                <p><strong>Intention:</strong> {formData.loan_usage_intention}</p>
                <p><strong>Businesses:</strong> {formData.businesses.length}</p>
                <p><strong>Guarantors:</strong> {formData.guarantors.length}</p>
                <p><strong>Collateral Items:</strong> {formData.client_collaterals.length}</p>
            </div>

            <button onClick={submitScreening} disabled={loading} className="w-full py-4 bg-green-600 text-white rounded-xl font-bold text-lg hover:bg-green-700 shadow-lg flex items-center justify-center gap-2">
                {loading ? 'Analyzing Risk...' : 'Submit Screening'}
                {!loading && <Activity className="w-6 h-6" />}
            </button>
        </div>
    );

    // --- MAIN RENDER ---
    const steps = [
        { id: 1, label: 'Client', icon: User },
        { id: 2, label: 'Debts', icon: CreditCard },
        { id: 3, label: 'Identity', icon: Shield },
        { id: 4, label: 'Spouse', icon: Users },
        { id: 5, label: 'Guarantor', icon: Users },
        { id: 6, label: 'Collateral', icon: Home },
        { id: 7, label: 'Household', icon: Home },
        { id: 8, label: 'Business', icon: Briefcase },
        { id: 9, label: 'Review', icon: CheckCircle },
    ];

    return (
        <div className="bg-white rounded-xl shadow-xl overflow-hidden max-w-5xl mx-auto">
            {/* Stepper Header */}
            <div className="bg-gray-50 border-b p-4 overflow-x-auto">
                <div className="flex items-center min-w-max space-x-4">
                    {steps.map((s) => (
                        <div key={s.id} className={`flex flex-col items-center cursor-pointer ${step === s.id ? 'text-blue-600' : 'text-gray-400'}`} onClick={() => setStep(s.id)}>
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${step === s.id ? 'border-blue-600 bg-blue-100' : 'border-gray-300 bg-white'}`}>
                                <s.icon className="w-5 h-5" />
                            </div>
                            <span className="text-xs font-medium mt-1">{s.label}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Form Content */}
            <div className="p-8 min-h-[500px]">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={step}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.2 }}
                    >
                        {step === 1 && renderStep1_ClientInfo()}
                        {step === 2 && renderStep2_InformalLoans()}
                        {step === 3 && renderStep3_Identity()}
                        {step === 4 && renderStep4_Spouse()}
                        {step === 5 && renderStep5_Guarantors()}
                        {step === 6 && renderStep6_Collaterals()}
                        {step === 7 && renderStep7_Household()}
                        {step === 8 && renderStep8_Business()}
                        {step === 9 && renderStep9_Review()}
                    </motion.div>
                </AnimatePresence>
            </div>

            {/* Footer Navigation */}
            <div className="bg-gray-50 border-t p-6 flex justify-between">
                <button
                    onClick={() => setStep(s => Math.max(1, s - 1))}
                    disabled={step === 1}
                    className={`px-6 py-2 rounded-lg font-medium ${step === 1 ? 'bg-gray-200 text-gray-400' : 'bg-white border hover:bg-gray-50 text-gray-700'}`}
                >
                    Previous
                </button>

                {step < 9 && (
                    <button
                        onClick={() => setStep(s => Math.min(9, s + 1))}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 shadow-md"
                    >
                        Next Step
                    </button>
                )}
            </div>
        </div>
    );
};

export default ClientScreeningForm;
