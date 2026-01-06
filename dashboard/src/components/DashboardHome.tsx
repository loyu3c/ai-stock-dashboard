import { useState, useEffect } from 'react';
import type { StockData } from '../types/stock';
import { api } from '../services/api';
import StockTable from './StockTable';
import AccountSwitcher from './AccountSwitcher';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';


const DashboardHome = () => {
    // const { stocks, loading, error } = useStocks(); // Switching to manual fetch for better control over parallel data
    const [stocks, setStocks] = useState<StockData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [accountStatus, setAccountStatus] = useState<any>(null);

    const fetchData = async () => {
        try {
            // Parallel fetch
            const [stockRes, statusRes] = await Promise.all([
                api.fetchAnalysisResults(),
                api.fetchAccountStatus()
            ]);

            setStocks(stockRes);
            setAccountStatus(statusRes);
        } catch (e: any) {
            console.error("Failed to fetch data:", e);
            setError(e.message || "Failed to load data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // Auto refresh every 30s
        return () => clearInterval(interval);
    }, []);

    // Stats
    const greenCount = stocks.filter(s => s.Signal === '🟢').length;
    const redCount = stocks.filter(s => s.Signal === '🔴').length;
    const yellowCount = stocks.filter(s => s.Signal === '🟡').length;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">🚀 AI 選股儀表板</h1>
                <AccountSwitcher onAccountChange={fetchData} />
            </div>

            {/* Asset Summary Card (Visible if account status loaded) */}
            {accountStatus && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <div>
                        <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">總資產 (Total Assets)</div>
                        <div className="text-2xl font-black text-slate-900">
                            {/* Simple approximation: Cash + Cost of Positions */}
                            TWD {Math.floor(accountStatus.balance + (accountStatus.positions?.reduce((sum: number, p: any) => sum + (p.quantity * p.avg_cost), 0) || 0)).toLocaleString()}
                        </div>
                    </div>
                    <div className="flex space-x-8">
                        <div>
                            <div className="text-xs text-slate-500 font-bold mb-1">現金餘額 (Cash)</div>
                            <div className="text-lg font-bold text-slate-700">TWD {Math.floor(accountStatus.balance).toLocaleString()}</div>
                        </div>
                        <div>
                            <div className="text-xs text-slate-500 font-bold mb-1">庫存市值 (Est. Value)</div>
                            <div className="text-lg font-bold text-slate-700">
                                {/* Ideally fetch current price, here using cost as fallback placeholder */}
                                TWD {Math.floor(accountStatus.positions?.reduce((sum: number, p: any) => sum + (p.quantity * p.avg_cost), 0) || 0).toLocaleString()}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="bg-white border-green-100 shadow-sm hover:shadow-md transition-shadow">
                    <CardHeader className="pb-2 border-b border-green-50">
                        <CardTitle className="text-green-600 flex items-center gap-2 text-lg">
                            <span className="p-1 bg-green-100 rounded-full text-xs">🟢</span> 買進訊號 (Buy)
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4">
                        <div className="text-4xl font-extrabold text-slate-800">{loading ? '-' : greenCount}</div>
                        <p className="text-xs text-slate-400 mt-2">Active opportunities</p>
                    </CardContent>
                </Card>

                <Card className="bg-white border-yellow-100 shadow-sm hover:shadow-md transition-shadow">
                    <CardHeader className="pb-2 border-b border-yellow-50">
                        <CardTitle className="text-yellow-600 flex items-center gap-2 text-lg">
                            <span className="p-1 bg-yellow-100 rounded-full text-xs">🟡</span> 觀望訊號 (Hold)
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4">
                        <div className="text-4xl font-extrabold text-slate-800">{loading ? '-' : yellowCount}</div>
                        <p className="text-xs text-slate-400 mt-2">Neutral outlook</p>
                    </CardContent>
                </Card>

                <Card className="bg-white border-red-100 shadow-sm hover:shadow-md transition-shadow">
                    <CardHeader className="pb-2 border-b border-red-50">
                        <CardTitle className="text-red-600 flex items-center gap-2 text-lg">
                            <span className="p-1 bg-red-100 rounded-full text-xs">🔴</span> 賣出訊號 (Sell)
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4">
                        <div className="text-4xl font-extrabold text-slate-800">{loading ? '-' : redCount}</div>
                        <p className="text-xs text-slate-400 mt-2">Caution required</p>
                    </CardContent>
                </Card>
            </div>

            {/* Main Table */}
            {error && <div className="bg-red-100 text-red-700 p-4 rounded">{error}. 請確認 .env 中的 CSV 連結是否正確。</div>}

            <StockTable data={stocks} loading={loading} accountBalance={accountStatus?.balance} />
        </div>
    );
};

export default DashboardHome;
// Updated to Light Theme

