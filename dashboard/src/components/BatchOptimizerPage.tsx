import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { FlaskConical, Play, Loader2, Check, ArrowUpDown, ReceiptText } from 'lucide-react';
import { api } from '../services/api';
import TradeDialog from './TradeDialog';


// Interfaces for optimization result
interface OptResult {
    best: {
        roi: number;
        win_rate: number;
        trades: number;
        params: any;
    };
    total_tested: number;
    last_run?: string;
    date_range?: string;
}

interface StockTask {
    code: string;
    name: string;
    status: 'idle' | 'running' | 'done' | 'error';
    progress: number; // 0-100
    msg: string;
    result?: OptResult;
    current_price?: number; // Added for trade dialog
}

const BatchOptimizerPage = () => {
    const [stocks, setStocks] = useState<StockTask[]>([]);
    const [accountStatus, setAccountStatus] = useState<any>(null);

    // Trade Dialog State
    const [selectedStock, setSelectedStock] = useState<StockTask | null>(null);
    const [isTradeOpen, setIsTradeOpen] = useState(false);

    // Sort State
    const [sortConfig, setSortConfig] = useState<{ key: string | null; direction: 'asc' | 'desc' }>({
        key: null,
        direction: 'asc',
    });

    const handleSort = (key: string) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const sortedStocks = [...stocks].sort((a, b) => {
        if (!sortConfig.key) return 0;
        const key = sortConfig.key;

        // Custom getters for simplified keys
        const getVal = (item: StockTask, k: string) => {
            if (k === 'code') return item.code;
            if (k === 'roi') return item.result?.best.roi || -999;
            if (k === 'win_rate') return item.result?.best.win_rate || 0;
            return 0;
        };

        const valA = getVal(a, key);
        const valB = getVal(b, key);

        if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
    });

    const renderSortHeader = (label: string, key: string) => (
        <th
            className="px-6 py-3 font-semibold cursor-pointer hover:bg-slate-100 transition-colors select-none"
            onClick={() => handleSort(key)}
        >
            <div className="flex items-center gap-1">
                {label}
                <ArrowUpDown size={14} className="text-slate-400" />
            </div>
        </th>
    );
    const [loading, setLoading] = useState(true);
    const [running, setRunning] = useState(false);

    // Date range (Default last 2 years)
    const today = new Date().toISOString().split('T')[0];
    const twoYearsAgo = new Date(new Date().setFullYear(new Date().getFullYear() - 2)).toISOString().split('T')[0];
    const [startDate, setStartDate] = useState(twoYearsAgo);
    const [endDate, setEndDate] = useState(today);

    useEffect(() => {
        fetchWatchlistAndHistory();
        api.fetchAccountStatus().then(setAccountStatus).catch(console.error);
    }, []);

    const fetchWatchlistAndHistory = async () => {
        try {
            setLoading(true);

            // 1. Fetch Watchlist & Analysis (for prices)
            const [configData, analysisData] = await Promise.all([
                api.fetchStockList(),
                api.fetchAnalysisResults()
            ]);

            if (!configData || !configData.stock_list) throw new Error("Invalid config data");

            // Create Price Map
            const priceMap: Record<string, number> = {};
            if (Array.isArray(analysisData)) {
                analysisData.forEach((s: any) => {
                    priceMap[s.Stock] = typeof s.Close === 'string' ? parseFloat(s.Close) : s.Close;
                });
            }

            // Filter enabled only?
            const stockData = configData.stock_list.filter((s: any) => s.Enabled === true || s.Enabled === "TRUE");

            // 2. Fetch Historical Results from Local Server JSON
            let history: any = {};
            try {
                history = await api.getOptimizerResults();
            } catch (err) {
                console.warn("Failed to fetch history", err);
            }

            // 3. Merge Data
            const initialTasks: StockTask[] = stockData.map((s: any) => {
                const saved = history[s.Stock]; // s.Stock is code
                return {
                    code: s.Stock,
                    name: s.Name,
                    status: saved ? 'done' : 'idle',
                    progress: saved ? 100 : 0,
                    msg: saved ? 'Optimization Complete (History)' : '等待執行',
                    result: saved || undefined,
                    current_price: priceMap[s.Stock] || 0
                };
            });

            setStocks(initialTasks);
        } catch (e) {
            console.error(e);
            alert("載入資料失敗");
        } finally {
            setLoading(false);
        }
    };

    const runOptimization = async (stockCode: string) => {
        // Update status to starting
        setStocks(prev => prev.map(s => s.code === stockCode ? { ...s, status: 'running', progress: 0, msg: '啟動中...', result: undefined } : s));

        try {
            // Force absolute URL to match api.ts fix
            const API_URL = "http://localhost:8000/api";

            const response = await fetch(`${API_URL}/optimize_stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stock: stockCode, start_date: startDate, end_date: endDate })
            });

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim() === '') continue;
                    try {
                        const event = JSON.parse(line);

                        setStocks(prev => prev.map(s => {
                            if (s.code !== stockCode) return s;

                            if (event.status === 'running') {
                                return { ...s, msg: event.msg, progress: event.progress };
                            } else if (event.status === 'done') {
                                return {
                                    ...s,
                                    status: 'done',
                                    msg: event.msg,
                                    progress: 100,
                                    result: event.result ? event.result : undefined
                                };
                            } else if (event.status === 'starting') {
                                return { ...s, msg: event.msg };
                            }
                            return s;
                        }));

                    } catch (err) {
                        console.error("JSON Parse Error", err);
                    }
                }
            }

        } catch (e: any) {
            console.error(e);
            setStocks(prev => prev.map(s => s.code === stockCode ? { ...s, status: 'error', msg: '錯誤: ' + e.message } : s));
        }
    };

    const runBatch = async () => {
        if (running) return;
        setRunning(true);
        for (const stock of stocks) {
            if (stock.status !== 'running') {
                await runOptimization(stock.code);
            }
        }
        setRunning(false);
    };

    const handleTradeClick = (stock: StockTask) => {
        setSelectedStock(stock);
        setIsTradeOpen(true);
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                        <FlaskConical className="text-indigo-600" /> 策略優化 (多股)
                    </h1>
                    <p className="text-slate-500 mt-1">AI 自動尋找波段交易最佳參數，包含 MA, RSI, KD 最佳組合。</p>
                </div>
                <div className="flex items-center gap-4 bg-white p-3 rounded-lg shadow-sm border border-slate-100">
                    <div className="flex items-center gap-2">
                        <label className="text-sm font-medium text-slate-600">開始:</label>
                        <input
                            type="date"
                            className="text-sm border rounded px-2 py-1 outline-none focus:ring-2 focus:ring-indigo-500"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <label className="text-sm font-medium text-slate-600">結束:</label>
                        <input
                            type="date"
                            className="text-sm border rounded px-2 py-1 outline-none focus:ring-2 focus:ring-indigo-500"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                        />
                    </div>
                    <button
                        onClick={runBatch}
                        disabled={running || loading}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium disabled:opacity-50 transition-all shadow-md active:scale-95"
                    >
                        {running ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
                        {running ? '執行中...' : '全部重新執行'}
                    </button>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>自選股優化清單 ({stocks.length})</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                                <tr>
                                    {renderSortHeader("代號", "code")}
                                    <th className="px-6 py-3 font-semibold">即時狀態</th>
                                    {renderSortHeader("ROI", "roi")}
                                    {renderSortHeader("勝率", "win_rate")}
                                    <th className="px-6 py-3 font-semibold">最佳參數 (MA/RSI/KD)</th>
                                    <th className="px-6 py-3 font-semibold">執行日期</th>
                                    <th className="px-6 py-3 font-semibold">資料範圍</th>
                                    <th className="px-6 py-3 font-semibold text-right">操作</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {sortedStocks.map((stock) => (
                                    <tr key={stock.code} className="bg-white hover:bg-slate-50">
                                        <td className="px-6 py-4">
                                            <div className="font-bold text-slate-700">{stock.code}</div>
                                            <div className="text-xs text-slate-500">{stock.name}</div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {stock.status === 'running' && (
                                                <div className="flex flex-col gap-1 w-24">
                                                    <div className="flex items-center gap-2 text-indigo-600 font-medium">
                                                        <Loader2 className="animate-spin" size={14} />
                                                        {Math.round(stock.progress)}%
                                                    </div>
                                                    <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                                                        <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${stock.progress}%` }}></div>
                                                    </div>
                                                    <div className="text-xs text-slate-400 truncate">{stock.msg}</div>
                                                </div>
                                            )}
                                            {stock.status === 'done' && (
                                                <div className="text-green-600 flex items-center gap-1 font-medium">
                                                    <Check size={14} /> 優化完成
                                                </div>
                                            )}
                                            {stock.status === 'error' && <div className="text-red-500">錯誤: {stock.msg}</div>}
                                            {stock.status === 'idle' && <div className="text-slate-400 text-xs">等待執行</div>}
                                        </td>
                                        <td className="px-6 py-4 font-mono font-bold">
                                            {stock.result ? <span className={stock.result.best.roi >= 0 ? 'text-green-600' : 'text-red-600'}>
                                                {stock.result.best.roi > 0 ? '+' : ''}{stock.result.best.roi.toFixed(2)}%
                                            </span> : '-'}
                                        </td>
                                        <td className="px-6 py-4">
                                            {stock.result ? (stock.result.best.win_rate).toFixed(1) + '%' : '-'}
                                        </td>
                                        <td className="px-6 py-4 text-xs font-mono text-slate-600">
                                            {stock.result ? (
                                                <div className="space-y-1">
                                                    <span className="block border border-slate-200 rounded px-1 w-fit bg-slate-50">
                                                        MA:{stock.result.best.params.MA_SHORT_DAYS || stock.result.best.params.ma_short}/{stock.result.best.params.MA_LONG_DAYS || stock.result.best.params.ma_long} RSI:{stock.result.best.params.RSI_THRESHOLD || stock.result.best.params.rsi_threshold} KD:{stock.result.best.params.KD_THRESHOLD || stock.result.best.params.kd_threshold}
                                                    </span>
                                                </div>
                                            ) : '-'}
                                        </td>
                                        <td className="px-6 py-4 text-xs text-slate-400">
                                            {stock.result?.last_run ? stock.result.last_run.split('T')[0] : '-'}
                                        </td>
                                        <td className="px-6 py-4 text-xs text-slate-400">
                                            {stock.result?.date_range || '-'}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex justify-end gap-2">
                                                <button
                                                    onClick={() => runOptimization(stock.code)}
                                                    disabled={stock.status === 'running'}
                                                    className="p-1.5 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors disabled:opacity-30"
                                                    title="重新執行優化"
                                                >
                                                    <Play size={18} />
                                                </button>
                                                <button
                                                    onClick={() => handleTradeClick(stock)}
                                                    className="p-1.5 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                                                    title="下單"
                                                >
                                                    <ReceiptText size={18} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>

            {selectedStock && (
                <TradeDialog
                    stockCode={selectedStock.code}
                    stockName={selectedStock.name}
                    currentPrice={selectedStock.current_price || 0}
                    isOpen={isTradeOpen}
                    onClose={() => setIsTradeOpen(false)}
                    accountBalance={accountStatus?.balance}
                    onOrderPlaced={() => api.fetchAccountStatus().then(setAccountStatus)}
                />
            )}
        </div>
    );
};

export default BatchOptimizerPage;
