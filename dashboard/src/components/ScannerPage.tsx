import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Search, Loader2, Plus, Check, ArrowUpDown, ReceiptText } from 'lucide-react';
import { api } from '../services/api';
import TradeDialog from './TradeDialog';

interface ScanResult {
    Stock: string;
    Name: string;
    Close: number;
    Signal: string;
    Memo: string;
    K: number;
    D: number;
    RSI: number;
    Volume: number;
}

export default function ScannerPage() {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<ScanResult[]>([]);
    const [scanLimit, setScanLimit] = useState(20);
    const [addedStocks, setAddedStocks] = useState<Set<string>>(new Set());
    const [accountStatus, setAccountStatus] = useState<any>(null);
    const [lastScanTime, setLastScanTime] = useState<string | null>(null);

    // Trade Dialog State
    const [selectedStock, setSelectedStock] = useState<ScanResult | null>(null);
    const [isTradeOpen, setIsTradeOpen] = useState(false);

    useEffect(() => {
        // Fetch account status for balance check
        api.fetchAccountStatus().then(setAccountStatus).catch(console.error);

        // Fetch last scan result
        api.fetchLastScanResult().then(data => {
            if (data && data.data) {
                setResults(data.data);
                setLastScanTime(data.timestamp);
            }
        }).catch(err => console.log("No previous scan result found or error:", err));
    }, []);

    // Sort State
    const [sortConfig, setSortConfig] = useState<{ key: keyof ScanResult | null; direction: 'asc' | 'desc' }>({
        key: null,
        direction: 'asc',
    });

    const handleSort = (key: keyof ScanResult) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const sortedResults = [...results].sort((a, b) => {
        if (!sortConfig.key) return 0;
        const key = sortConfig.key;
        if (a[key] < b[key]) return sortConfig.direction === 'asc' ? -1 : 1;
        if (a[key] > b[key]) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
    });

    const renderSortHeader = (label: string, key: keyof ScanResult) => (
        <th
            className="px-4 py-3 cursor-pointer hover:bg-slate-100 transition-colors select-none"
            onClick={() => handleSort(key)}
        >
            <div className="flex items-center gap-1">
                {label}
                <ArrowUpDown size={14} className="text-slate-400" />
            </div>
        </th>
    );

    const handleScan = async () => {
        setLoading(true);
        setResults([]);
        try {
            const data = await api.scanMarket('volume_rank', scanLimit);
            setResults(data);
            // Update time locally
            const now = new Date();
            const timeStr = now.getFullYear() + "-" +
                String(now.getMonth() + 1).padStart(2, '0') + "-" +
                String(now.getDate()).padStart(2, '0') + " " +
                String(now.getHours()).padStart(2, '0') + ":" +
                String(now.getMinutes()).padStart(2, '0') + ":" +
                String(now.getSeconds()).padStart(2, '0');
            setLastScanTime(timeStr);
        } catch (error) {
            console.error(error);
            alert("掃描失敗，請確認後端 Server 是否執行中");
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async (stock: ScanResult) => {
        try {
            const payload = {
                Stock: stock.Stock,
                Name: stock.Name,
                Enabled: true,
                Memo: stock.Memo
            };

            const res = await api.addStock(payload);

            if (res.status === 'success' || res.status === 'skipped') {
                setAddedStocks(prev => new Set(prev).add(stock.Stock));
            } else {
                alert("加入失敗");
            }

        } catch (error) {
            console.error(error);
            alert("加入失敗");
        }
    };

    const handleTradeClick = (stock: ScanResult) => {
        setSelectedStock(stock);
        setIsTradeOpen(true);
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-extrabold mb-8 text-slate-800 tracking-tight flex items-center gap-3">
                <Search className="w-8 h-8 text-blue-600" />
                市場掃描 (Scanner)
                {lastScanTime && (
                    <span className="text-sm font-normal text-slate-500 ml-auto bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
                        🕒 上次掃描: {lastScanTime}
                    </span>
                )}
            </h1>

            <Card className="shadow-lg border-0 bg-white/50 backdrop-blur-sm">
                <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                        <span>🚀 潛力股挖掘</span>
                        <div className="flex items-center gap-3">
                            <select
                                className="border rounded px-3 py-2 text-sm bg-white"
                                value={scanLimit}
                                onChange={(e) => setScanLimit(Number(e.target.value))}
                            >
                                <option value={10}>成交量前 10 名</option>
                                <option value={20}>成交量前 20 名</option>
                                <option value={50}>成交量前 50 名 (較慢)</option>
                            </select>

                            <button
                                onClick={handleScan}
                                disabled={loading}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium disabled:opacity-50 transition-all shadow-md active:scale-95"
                            >
                                {loading ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />}
                                {loading ? '掃描中...' : '開始掃描'}
                            </button>
                        </div>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {!loading && results.length === 0 && (
                        <div className="text-center py-12 text-slate-400">
                            <Search className="w-16 h-16 mx-auto mb-4 opacity-20" />
                            <p>點擊上方按鈕開始掃描市場熱門股</p>
                        </div>
                    )}

                    {loading && (
                        <div className="text-center py-20 text-blue-600">
                            <Loader2 className="w-12 h-12 mx-auto mb-4 animate-spin text-blue-400" />
                            <p className="animate-pulse">正在從全市場挖掘潛力股，請稍候...</p>
                        </div>
                    )}

                    {results.length > 0 && (
                        <div className="overflow-x-auto rounded-lg border border-slate-100 shadow-sm">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                                    <tr>
                                        {renderSortHeader("代號", "Stock")}
                                        {renderSortHeader("名稱", "Name")}
                                        {renderSortHeader("收盤", "Close")}
                                        {renderSortHeader("成交量", "Volume")}
                                        {renderSortHeader("訊號", "Signal")}
                                        <th className="px-4 py-3 text-center">操作</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100 bg-white">
                                    {sortedResults.map((stock) => {
                                        const isAdded = addedStocks.has(stock.Stock);
                                        return (
                                            <tr key={stock.Stock} className="hover:bg-slate-50 transition-colors">
                                                <td className="px-4 py-3 font-medium text-slate-700">{stock.Stock}</td>
                                                <td className="px-4 py-3">{stock.Name}</td>
                                                <td className="px-4 py-3 font-mono">{stock.Close}</td>
                                                <td className="px-4 py-3 font-mono text-slate-600">{(stock.Volume || 0).toLocaleString()}</td>
                                                <td className="px-4 py-3 text-lg">{stock.Signal}</td>
                                                <td className="px-4 py-3 text-center">
                                                    <div className="flex justify-center gap-2">
                                                        <button
                                                            onClick={() => handleAdd(stock)}
                                                            disabled={isAdded}
                                                            className={`px-3 py-1.5 rounded-md flex items-center gap-1 transition-all ${isAdded
                                                                ? 'bg-green-100 text-green-700 cursor-default'
                                                                : 'bg-blue-50 text-blue-600 hover:bg-blue-100 hover:scale-105 active:scale-95'
                                                                }`}
                                                        >
                                                            {isAdded ? (
                                                                <>
                                                                    <Check size={14} /> 已加入
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <Plus size={14} /> 加入
                                                                </>
                                                            )}
                                                        </button>

                                                        <button
                                                            onClick={() => handleTradeClick(stock)}
                                                            className="px-3 py-1.5 rounded-md flex items-center gap-1 bg-slate-50 text-slate-600 hover:bg-slate-100 hover:text-slate-800 transition-all active:scale-95 border border-slate-200"
                                                        >
                                                            <ReceiptText size={14} /> 下單
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>

            {selectedStock && (
                <TradeDialog
                    stockCode={selectedStock.Stock}
                    stockName={selectedStock.Name}
                    currentPrice={selectedStock.Close}
                    isOpen={isTradeOpen}
                    onClose={() => setIsTradeOpen(false)}
                    accountBalance={accountStatus?.balance}
                    onOrderPlaced={() => api.fetchAccountStatus().then(setAccountStatus)} // Refresh balance
                />
            )}
        </div>
    );
}
