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
            <h1 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white">🚀 AI 選股儀表板</h1>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-green-50 border-green-200">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-green-700">🟢 買進訊號 (Buy)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-4xl font-bold text-green-800">{loading ? '-' : greenCount}</div>
                    </CardContent>
                </Card>

                <Card className="bg-yellow-50 border-yellow-200">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-yellow-700">🟡 觀望訊號 (Hold)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-4xl font-bold text-yellow-800">{loading ? '-' : yellowCount}</div>
                    </CardContent>
                </Card>

                <Card className="bg-red-50 border-red-200">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-red-700">🔴 賣出訊號 (Sell)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-4xl font-bold text-red-800">{loading ? '-' : redCount}</div>
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
