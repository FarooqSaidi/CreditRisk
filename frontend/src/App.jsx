import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import LoanExplorer from './components/LoanExplorer';
import BorrowerProfiles from './components/BorrowerProfiles';
import BorrowerDetail from './components/BorrowerDetail';
import AdvancedAnalytics from './components/AdvancedAnalytics';
import ClientScreeningPage from './components/ClientScreeningPage';

const PageTransition = ({ children }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
    >
        {children}
    </motion.div>
);

const AnimatedRoutes = () => {
    const location = useLocation();

    return (
        <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
                <Route path="/" element={<PageTransition><Dashboard /></PageTransition>} />
                <Route path="/loans" element={<PageTransition><LoanExplorer /></PageTransition>} />
                <Route path="/borrowers" element={<PageTransition><BorrowerProfiles /></PageTransition>} />
                <Route path="/borrowers/:id" element={<PageTransition><BorrowerDetail /></PageTransition>} />
                <Route path="/analytics" element={<PageTransition><AdvancedAnalytics /></PageTransition>} />
                <Route path="/screening" element={<PageTransition><ClientScreeningPage /></PageTransition>} />
            </Routes>
        </AnimatePresence>
    );
};

function App() {
    return (
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <Layout>
                <AnimatedRoutes />
            </Layout>
        </Router>
    );
}

export default App;
