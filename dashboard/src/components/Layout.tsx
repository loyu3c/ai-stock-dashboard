import { useState } from 'react';
import { Menu } from 'lucide-react';
import Sidebar from './Sidebar';
import DashboardHome from './DashboardHome';
import ConfigPage from './ConfigPage';

const Layout = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const renderContent = () => {
        switch (activeTab) {
            case 'dashboard':
                return <DashboardHome />;
            case 'scanner':
                return <div className="p-8 text-center text-gray-500">🚧 市場掃描頁面開發中...</div>;
            case 'backtest':
                return <div className="p-8 text-center text-gray-500">🚧 回測分析頁面開發中...</div>;
            case 'settings':
                return <ConfigPage />;
            default:
                return <DashboardHome />;
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
            {/* Mobile Header */}
            <div className="md:hidden bg-white border-b border-slate-100 p-4 flex items-center justify-between sticky top-0 z-30">
                <div className="flex items-center gap-2">
                    <span className="text-xl">🚀</span>
                    <span className="font-bold text-slate-800">AI Stock</span>
                </div>
                <button
                    onClick={() => setIsSidebarOpen(true)}
                    className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                    <Menu size={24} />
                </button>
            </div>

            {/* Sidebar */}
            <Sidebar
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                isOpen={isSidebarOpen}
                onClose={() => setIsSidebarOpen(false)}
            />

            {/* Main Content Area */}
            <main className="flex-1 md:ml-64 p-4 md:p-8 overflow-y-auto">
                {renderContent()}
            </main>
        </div>
    );
};

export default Layout;
