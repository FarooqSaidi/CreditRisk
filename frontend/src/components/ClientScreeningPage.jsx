import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ClientScreeningForm from './ClientScreeningForm';
import ScreeningDashboard from './ScreeningDashboard';

const ClientScreeningPage = () => {
    const [screeningResult, setScreeningResult] = useState(null);
    const [borrowerId, setBorrowerId] = useState(1); // Default to first borrower for demo

    const handleComplete = (result) => {
        setScreeningResult(result);
    };

    const handleReset = () => {
        setScreeningResult(null);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Client Screening & Risk Assessment</h1>
                    <p className="text-gray-600 mt-2">
                        AI-powered tool for evaluating borrower risk, detecting hidden obligations, and recommending loan limits.
                    </p>
                </header>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    {!screeningResult ? (
                        <ClientScreeningForm
                            borrowerId={borrowerId}
                            onComplete={handleComplete}
                        />
                    ) : (
                        <ScreeningDashboard
                            result={screeningResult}
                            onReset={handleReset}
                        />
                    )}
                </motion.div>
            </div>
        </div>
    );
};

export default ClientScreeningPage;
