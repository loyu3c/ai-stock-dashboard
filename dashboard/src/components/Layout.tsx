import { useState } from 'react';
import Sidebar from './Sidebar';
import DashboardHome from './DashboardHome';

const Layout = () => {
    const [activeTab, setActiveTab] = useState('dashboard');

    const renderContent = () => {
        switch (activeTab) {
            case 'dashboard':
                return <DashboardHome />;
            case 'scanner':
                return <div className="p-8 text-center text-gray-500">🚧 市場掃描頁面開發中...</div>;
            case 'backtest':
                return <div className="p-8 text-center text-gray-500">🚧 回測分析頁面開發中...</div>;
            case 'settings':
                return <div className="p-8 text-center text-gray-500">🚧 系統設定頁面開發中...</div>;
            default:
                return <DashboardHome />;
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex">
            {/* Sidebar */}
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

            {/* Main Content Area */}
            <main className="flex-1 ml-64 p-8 overflow-y-auto">
                {renderContent()}
            </main>
        </div>
    );
};

export default Layout;
