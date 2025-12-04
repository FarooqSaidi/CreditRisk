import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const endpoints = {
    branches: '/branches/',
    loans: '/loans/',
    borrowers: '/borrowers/',
    riskMetrics: {
        group: '/risk-metrics/group/',
        loan: '/risk-metrics/loan/',
    },
    models: {
        train: '/models/train/',
        predict: '/models/predict/',
    },
    stats: {
        loans: '/loans/statistics/',
        portfolio: '/loans/portfolio_metrics/',
        repayments: '/repayments/statistics/',
    }
};

export default api;
