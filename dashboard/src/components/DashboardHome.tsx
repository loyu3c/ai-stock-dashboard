import { useStocks } from '../hooks/useStocks';
import StockTable from './StockTable';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

const DashboardHome = () => {
    const { stocks, loading, error } = useStocks();

    // Stats
    const greenCount = stocks.filter(s => s.Signal === '🟢').length;
    const redCount = stocks.filter(s => s.Signal === '🔴').length;
    const yellowCount = stocks.filter(s => s.Signal === '🟡').length;

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-extrabold mb-8 text-slate-800 tracking-tight">🚀 AI 選股儀表板</h1>

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

            <StockTable data={stocks} loading={loading} />
        </div>
    );
};

export default DashboardHome;
// Updated to Light Theme

