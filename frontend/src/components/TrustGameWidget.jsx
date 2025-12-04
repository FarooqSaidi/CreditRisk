import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Heart, Shield, Coins, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';

const TrustGameWidget = ({ type, onComplete }) => {
    // type: 'SPOUSE' or 'GUARANTOR'
    const [step, setStep] = useState(0);
    const [answers, setAnswers] = useState({});
    const [score, setScore] = useState(null);
    const [recommendation, setRecommendation] = useState(null);

    const questions = type === 'SPOUSE' ? [
        {
            id: 'q1',
            text: "Financial Transparency Test",
            description: "The client receives an unexpected MWK 50,000 from a side business deal. Does the spouse know about this money?",
            type: 'choice',
            options: [
                { value: 0, label: "No, spouse has no idea about the money", risk: "HIGH" },
                { value: 30, label: "Spouse suspects but wasn't told directly", risk: "MEDIUM" },
                { value: 70, label: "Spouse knows but not the exact amount", risk: "LOW" },
                { value: 100, label: "Spouse knows everything and helped count it", risk: "VERY LOW" }
            ],
            weight: 0.25
        },
        {
            id: 'q2',
            text: "Repayment Crisis Response",
            description: "It's loan repayment day but the business made only MWK 15,000 instead of the needed MWK 25,000. What does the spouse do?",
            type: 'choice',
            options: [
                { value: 0, label: "Refuses to help - 'It's your loan, not mine'", risk: "REJECT" },
                { value: 20, label: "Complains but does nothing to help", risk: "HIGH" },
                { value: 60, label: "Offers MWK 5,000 from personal savings reluctantly", risk: "MEDIUM" },
                { value: 100, label: "Immediately sells personal items or borrows to cover the gap", risk: "LOW" }
            ],
            weight: 0.30
        },
        {
            id: 'q3',
            text: "Joint Responsibility Awareness",
            description: "Ask the spouse directly: 'If your partner cannot pay this loan, who is responsible?'",
            type: 'choice',
            options: [
                { value: 0, label: "The bank's problem / Not my concern", risk: "REJECT" },
                { value: 30, label: "My partner alone must handle it", risk: "HIGH" },
                { value: 70, label: "I would try to help but it's mainly their responsibility", risk: "MEDIUM" },
                { value: 100, label: "We are both responsible - I will do whatever it takes", risk: "LOW" }
            ],
            weight: 0.25
        },
        {
            id: 'q4',
            text: "Loan Purpose Alignment",
            description: "Does the spouse agree with how the loan money will be used?",
            type: 'choice',
            options: [
                { value: 0, label: "Strongly disagrees - thinks it's a bad idea", risk: "REJECT" },
                { value: 40, label: "Has concerns but won't interfere", risk: "HIGH" },
                { value: 75, label: "Neutral - trusts partner's judgment", risk: "MEDIUM" },
                { value: 100, label: "Fully supports and will actively help with the business", risk: "LOW" }
            ],
            weight: 0.20
        }
    ] : [
        {
            id: 'q1',
            text: "Relationship Depth Test",
            description: "How long have the guarantor and client known each other, and what is their relationship?",
            type: 'choice',
            options: [
                { value: 0, label: "Less than 6 months / Just met recently", risk: "REJECT" },
                { value: 30, label: "1-2 years / Casual acquaintance", risk: "HIGH" },
                { value: 70, label: "3-5 years / Good friend or distant relative", risk: "MEDIUM" },
                { value: 100, label: "5+ years / Close family or lifelong friend", risk: "LOW" }
            ],
            weight: 0.20
        },
        {
            id: 'q2',
            text: "Financial Commitment Test",
            description: "The client defaults on MWK 30,000. The guarantor is asked to pay immediately. What happens?",
            type: 'choice',
            options: [
                { value: 0, label: "Refuses completely - 'I only signed, I won't pay'", risk: "REJECT" },
                { value: 20, label: "Says they'll pay but keeps delaying", risk: "HIGH" },
                { value: 60, label: "Pays MWK 10,000 now, promises rest later", risk: "MEDIUM" },
                { value: 100, label: "Pays the full amount within 1 week", risk: "LOW" }
            ],
            weight: 0.35
        },
        {
            id: 'q3',
            text: "Asset Pledge Willingness",
            description: "Ask the guarantor: 'Can you pledge your [bicycle/goat/TV] as security for this loan right now?'",
            type: 'choice',
            options: [
                { value: 0, label: "Refuses - 'I can't risk my property'", risk: "HIGH" },
                { value: 40, label: "Hesitates and asks for time to think", risk: "MEDIUM" },
                { value: 100, label: "Agrees immediately and shows the asset", risk: "LOW" }
            ],
            weight: 0.25
        },
        {
            id: 'q4',
            text: "Tracking & Enforcement Ability",
            description: "If the client disappears or moves without paying, what will the guarantor do?",
            type: 'choice',
            options: [
                { value: 0, label: "Nothing - doesn't know where client lives or works", risk: "REJECT" },
                { value: 30, label: "Will call client's family but can't do more", risk: "HIGH" },
                { value: 70, label: "Knows client's village and will visit to find them", risk: "MEDIUM" },
                { value: 100, label: "Lives in same village, knows family, can physically track client", risk: "LOW" }
            ],
            weight: 0.20
        }
    ];

    const handleAnswer = (value) => {
        const currentQ = questions[step];
        setAnswers(prev => ({ ...prev, [currentQ.id]: value }));
    };

    const nextStep = () => {
        if (step < questions.length - 1) {
            setStep(step + 1);
        } else {
            calculateScore();
        }
    };

    const calculateScore = () => {
        let totalScore = 0;
        let totalWeight = 0;
        let hasRejectFlag = false;
        let highRiskCount = 0;

        questions.forEach(q => {
            let val = answers[q.id];
            const selectedOption = q.options?.find(opt => opt.value === val);

            // Check for rejection flags
            if (selectedOption?.risk === 'REJECT') {
                hasRejectFlag = true;
            }
            if (selectedOption?.risk === 'HIGH') {
                highRiskCount++;
            }

            totalScore += val * q.weight;
            totalWeight += q.weight;
        });

        const finalScore = Math.round(totalScore);
        setScore(finalScore);

        // Determine recommendation
        let rec = {};
        if (hasRejectFlag) {
            rec = {
                decision: 'REJECT',
                reason: 'Critical red flag detected - high default risk',
                loanMultiplier: 0,
                color: 'red'
            };
        } else if (finalScore < 40 || highRiskCount >= 2) {
            rec = {
                decision: 'REJECT',
                reason: 'Trust score too low - insufficient commitment',
                loanMultiplier: 0,
                color: 'red'
            };
        } else if (finalScore < 60) {
            rec = {
                decision: 'CONDITIONAL',
                reason: 'Moderate risk - reduce loan amount by 40%',
                loanMultiplier: 0.6,
                color: 'yellow'
            };
        } else if (finalScore < 80) {
            rec = {
                decision: 'ACCEPT',
                reason: 'Good trust level - reduce loan amount by 20%',
                loanMultiplier: 0.8,
                color: 'blue'
            };
        } else {
            rec = {
                decision: 'ACCEPT',
                reason: 'Excellent trust level - approve full amount',
                loanMultiplier: 1.0,
                color: 'green'
            };
        }

        setRecommendation(rec);
        if (onComplete) onComplete({ score: finalScore, recommendation: rec });
    };

    const currentQ = questions[step];

    if (score !== null && recommendation) {
        const bgColor = {
            red: 'bg-red-50 border-red-300',
            yellow: 'bg-yellow-50 border-yellow-300',
            blue: 'bg-blue-50 border-blue-300',
            green: 'bg-green-50 border-green-300'
        }[recommendation.color];

        const iconColor = {
            red: 'text-red-600',
            yellow: 'text-yellow-600',
            blue: 'text-blue-600',
            green: 'text-green-600'
        }[recommendation.color];

        const Icon = recommendation.decision === 'REJECT' ? XCircle : CheckCircle2;

        return (
            <div className={`${bgColor} p-6 rounded-xl border-2`}>
                <div className="flex items-start gap-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${bgColor}`}>
                        <Icon className={`w-7 h-7 ${iconColor}`} />
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-lg font-bold text-gray-900">
                                {type === 'SPOUSE' ? 'Spouse Trust Assessment' : 'Guarantor Trust Assessment'}
                            </h3>
                            <span className={`text-2xl font-bold ${iconColor}`}>{score}/100</span>
                        </div>
                        
                        <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mb-3 ${
                            recommendation.decision === 'REJECT' ? 'bg-red-100 text-red-800' :
                            recommendation.decision === 'CONDITIONAL' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                        }`}>
                            {recommendation.decision}
                        </div>

                        <p className="text-gray-700 mb-3">{recommendation.reason}</p>

                        {recommendation.decision !== 'REJECT' && (
                            <div className="bg-white bg-opacity-60 p-3 rounded-lg">
                                <p className="text-sm font-medium text-gray-900">
                                    Loan Amount Adjustment: <span className={`font-bold ${iconColor}`}>
                                        {(recommendation.loanMultiplier * 100).toFixed(0)}%
                                    </span> of requested amount
                                </p>
                            </div>
                        )}

                        <button
                            onClick={() => { 
                                setStep(0); 
                                setScore(null); 
                                setRecommendation(null); 
                                setAnswers({}); 
                            }}
                            className="mt-4 text-sm text-gray-600 hover:text-gray-900 hover:underline"
                        >
                            Retake Assessment
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                    {type === 'SPOUSE' ? <Heart className="w-5 h-5 text-pink-500" /> : <Shield className="w-5 h-5 text-blue-500" />}
                    {type === 'SPOUSE' ? 'Couples Trust Game' : 'Guarantor Trust Game'}
                </h3>
                <span className="text-xs font-medium px-2 py-1 bg-slate-100 rounded-full text-slate-600">
                    Step {step + 1} of {questions.length}
                </span>
            </div>

            <div className="mb-8">
                <h4 className="text-lg font-medium text-slate-900 mb-2">{currentQ.text}</h4>
                <p className="text-slate-500 text-sm mb-6">{currentQ.description}</p>

                <div className="grid grid-cols-1 gap-3">
                    {currentQ.options.map((opt) => {
                        const isSelected = answers[currentQ.id] === opt.value;
                        const riskColor = {
                            'REJECT': 'border-red-300 hover:border-red-400',
                            'HIGH': 'border-orange-300 hover:border-orange-400',
                            'MEDIUM': 'border-yellow-300 hover:border-yellow-400',
                            'LOW': 'border-green-300 hover:border-green-400',
                            'VERY LOW': 'border-emerald-300 hover:border-emerald-400'
                        }[opt.risk] || 'border-slate-200 hover:border-blue-300';

                        const riskBadge = {
                            'REJECT': 'bg-red-100 text-red-700',
                            'HIGH': 'bg-orange-100 text-orange-700',
                            'MEDIUM': 'bg-yellow-100 text-yellow-700',
                            'LOW': 'bg-green-100 text-green-700',
                            'VERY LOW': 'bg-emerald-100 text-emerald-700'
                        }[opt.risk];

                        return (
                            <button
                                key={opt.label}
                                onClick={() => handleAnswer(opt.value)}
                                className={`p-4 rounded-lg border-2 text-left transition-all ${
                                    isSelected
                                        ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500'
                                        : riskColor
                                }`}
                            >
                                <div className="flex items-start justify-between gap-3">
                                    <span className="flex-1 text-sm font-medium text-gray-900">{opt.label}</span>
                                    <span className={`text-xs px-2 py-1 rounded-full font-semibold whitespace-nowrap ${riskBadge}`}>
                                        {opt.risk}
                                    </span>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>

            <div className="flex justify-end">
                <button
                    onClick={nextStep}
                    disabled={answers[currentQ.id] === undefined}
                    className="px-6 py-2 bg-slate-900 text-white rounded-lg font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {step === questions.length - 1 ? 'Calculate Score' : 'Next Scenario'}
                </button>
            </div>
        </div>
    );
};

export default TrustGameWidget;
