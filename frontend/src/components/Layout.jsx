import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, CreditCard, PieChart, Settings, Shield } from 'lucide-react';
import clsx from 'clsx';

const Layout = ({ children }) => {
    const location = useLocation();

    const navItems = [
        { name: 'Dashboard', path: '/', icon: LayoutDashboard },
        { name: 'Loans', path: '/loans', icon: CreditCard },
        { name: 'Borrowers', path: '/borrowers', icon: Users },
        { name: 'Analytics', path: '/analytics', icon: PieChart },
        { name: 'Screening', path: '/screening', icon: Shield },
    ];

    return (
        <div className="min-h-screen bg-slate-50 flex">
            {/* Sidebar */}
            <div className="w-64 bg-slate-900 text-white fixed h-full">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-malawi-red">CreditRisk<span className="text-white">MW</span></h1>
                    <p className="text-xs text-slate-400 mt-1">Malawi Microfinance Analytics</p>
                </div>

                <nav className="mt-6 px-4">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={clsx(
                                "flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors",
                                location.pathname === item.path
                                    ? "bg-malawi-red text-white"
                                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                            )}
                        >
                            <item.icon size={20} />
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    ))}
                </nav>

                <div className="absolute bottom-0 w-full p-4 border-t border-slate-800">
                    <div className="flex items-center gap-3 text-slate-400">
                        <div className="w-8 h-8 rounded-full bg-malawi-green flex items-center justify-center text-white font-bold">
                            FS
                        </div>
                        <div>
                            <p className="text-sm font-medium text-white">Farooq Saidi</p>
                            <p className="text-xs">Admin</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="ml-64 flex-1">
                <header className="bg-white shadow-sm h-16 flex items-center justify-between px-8">
                    <h2 className="text-xl font-semibold text-slate-800">
                        {navItems.find(i => i.path === location.pathname)?.name || 'Credit Risk'}
                    </h2>
                    <div className="flex items-center gap-4">
                        <span className="text-sm text-slate-500">Last updated: {new Date().toLocaleDateString()}</span>
                    </div>
                </header>

                <main className="p-8">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default Layout;
