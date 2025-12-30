import { LayoutDashboard, TrendingUp, Settings, LineChart } from 'lucide-react';
import { cn } from '../lib/utils';

interface MenuItem {
    icon: React.ElementType;
    label: string;
    id: string;
}

const menuItems: MenuItem[] = [
    { icon: LayoutDashboard, label: '總覽看板', id: 'dashboard' },
    { icon: TrendingUp, label: '市場掃描 (Scanner)', id: 'scanner' },
    { icon: LineChart, label: '回測分析 (Backtest)', id: 'backtest' },
    { icon: Settings, label: '系統設定', id: 'settings' },
];

interface SidebarProps {
    activeTab: string;
    setActiveTab: (id: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
    return (
        <div className="h-screen w-64 bg-slate-900 text-white flex flex-col fixed left-0 top-0">
            <div className="p-6 border-b border-slate-700">
                <h1 className="text-xl font-bold flex items-center gap-2">
                    🚀 AI Stock
                </h1>
                <p className="text-xs text-slate-400 mt-1">波段選股小幫手</p>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {menuItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={cn(
                            "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-sm font-medium",
                            activeTab === item.id
                                ? "bg-blue-600 text-white shadow-md shadow-blue-900/20"
                                : "text-slate-300 hover:bg-slate-800 hover:text-white"
                        )}
                    >
                        <item.icon size={20} />
                        {item.label}
                    </button>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
                v1.0.0
            </div>
        </div>
    );
};

export default Sidebar;
