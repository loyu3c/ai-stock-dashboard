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
    isOpen: boolean;
    onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isOpen, onClose }) => {
    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/20 z-40 md:hidden backdrop-blur-sm"
                    onClick={onClose}
                />
            )}

            {/* Sidebar Container */}
            <div className={cn(
                "h-screen w-64 bg-white text-slate-800 border-r border-slate-100 flex flex-col fixed left-0 top-0 shadow-xl transition-transform duration-300 z-50",
                // Mobile: Off-screen by default (-translate-x-full), visible if isOpen
                // Desktop: Always visible (translate-x-0)
                "md:translate-x-0",
                isOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                    <div>
                        <h1 className="text-xl font-extrabold flex items-center gap-2 text-blue-600 tracking-tight">
                            🚀 AI Stock
                        </h1>
                        <p className="text-xs text-slate-400 mt-1 font-medium">波段選股小幫手</p>
                    </div>
                    {/* Mobile Close Button */}
                    <button onClick={onClose} className="md:hidden text-slate-400 hover:text-slate-600">
                        ✕
                    </button>
                </div>

                <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                    {menuItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => {
                                setActiveTab(item.id);
                                onClose(); // Close on click (mobile)
                            }}
                            className={cn(
                                "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-sm font-semibold group",
                                activeTab === item.id
                                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30 translate-y-[-1px]"
                                    : "text-slate-500 hover:bg-blue-50 hover:text-blue-700"
                            )}
                        >
                            <item.icon size={20} className={cn("transition-colors", activeTab !== item.id && "text-slate-400 group-hover:text-blue-600")} />
                            {item.label}
                        </button>
                    ))}
                </nav>

                <div className="p-4 border-t border-slate-100">
                    <div className="bg-slate-50 rounded-lg p-3 text-center">
                        <p className="text-xs text-slate-400 font-medium">Auto-Sync Enabled</p>
                        <p className="text-[10px] text-slate-300 mt-1">v1.1.0 (Mobile)</p>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Sidebar;
