import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { LineChart, Play, Loader2, TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';
import { api } from '../services/api';
import {
    ComposedChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';

interface BacktestSummary {
    total_return_pct: number;
    start_capital: number;
    end_capital: number;
    total_trades: number;
    win_count: number;
    loss_count: number;
    win_rate: number;
}

interface Trade {
    date: string;
    type: string;
    price: number;
    profit?: number;
    profit_pct?: number;
    reason: string;
}

interface DailyData {
    date: string;
    equity: number;
    price: number;
    signal: string | null;
}

interface BacktestResult {
    stock: string;
    summary: BacktestSummary;
    trades: Trade[];
    daily_history: DailyData[];
}

export default function BacktestPage() {
    const today = new Date().toISOString().split('T')[0];
    const lastYear = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).toISOString().split('T')[0];

    const [stockCode, setStockCode] = useState('2330');
    const [startDate, setStartDate] = useState(lastYear);
    const [endDate, setEndDate] = useState(today);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<BacktestResult | null>(null);
    const [optResult, setOptResult] = useState<any | null>(null);

    const handleRunBacktest = async (overrideParams?: any) => {
        if (!stockCode) return;
        setLoading(true);
        setResult(null);
        try {
            const body: any = {
                stock: stockCode,
                start_date: startDate,
                end_date: endDate
            };
            if (overrideParams) {
                body.strategy_override = overrideParams;
            }

            const data = await api.runBacktest(body);
            setResult(data);

        } catch (error: any) {
            console.error(error);
            alert("回測失敗: " + error.message);
        } finally {
            setLoading(false);
        }
    };

    // Custom Dot for Chart Signals
    const renderCustomizedDot = (props: any) => {
        const { cx, cy, payload } = props;
        if (payload.signal === '🟢') {
            return (
                <text x={cx} y={cy - 10} textAnchor="middle" fontSize="16">🟢</text>
            );
        }
        if (payload.signal === '🔴') {
            return (
                <text x={cx} y={cy - 10} textAnchor="middle" fontSize="16">🔴</text>
            );
        }
        return null;
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-extrabold mb-8 text-slate-800 tracking-tight flex items-center gap-3">
                <LineChart className="w-8 h-8 text-indigo-600" />
                回測分析 (Backtest)
            </h1>

            {/* Input Config */}
            <Card className="shadow-md border-0 bg-white/50 backdrop-blur-sm">
                <CardHeader>
                    <CardTitle>⚙️ 回測設定</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col md:flex-row gap-4 items-end">
                        <div className="w-full md:w-1/4">
                            <label className="block text-xs font-medium text-slate-500 mb-1">股票代號</label>
                            <input
                                type="text"
                                className="w-full border rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-blue-200 outline-none transition-all font-mono"
                                value={stockCode}
                                onChange={(e) => setStockCode(e.target.value)}
                                placeholder="e.g. 2330"
                            />
                        </div>
                        <div className="w-full md:w-1/4">
                            <label className="block text-xs font-medium text-slate-500 mb-1">開始日期</label>
                            <input
                                type="date"
                                className="w-full border rounded-lg px-3 py-2 bg-white"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                            />
                        </div>
                        <div className="w-full md:w-1/4">
                            <label className="block text-xs font-medium text-slate-500 mb-1">結束日期</label>
                            <input
                                type="date"
                                className="w-full border rounded-lg px-3 py-2 bg-white"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                            />
                        </div>
                        <div className="w-full md:w-auto">
                            <button
                                onClick={() => handleRunBacktest()}
                                disabled={loading}
                                className="w-full md:w-auto bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg flex items-center justify-center gap-2 font-medium disabled:opacity-50 transition-all shadow-md active:scale-95 whitespace-nowrap"
                            >
                                {loading ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
                                {loading ? '計算中...' : '執行回測'}
                            </button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Optimization Section */}
            <div className="space-y-4">
                <div className="flex justify-end">
                    <button
                        onClick={async () => {
                            if (!stockCode) return;
                            setLoading(true);
                            setOptResult(null);
                            try {
                                const data = await api.optimizeStrategy({ stock: stockCode, start_date: startDate, end_date: endDate });
                                setOptResult(data);
                            } catch (e) {
                                alert("優化失敗: " + e);
                            } finally {
                                setLoading(false);
                            }
                        }}
                        disabled={loading}
                        className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1 font-medium px-4 py-2 hover:bg-indigo-50 rounded-lg transition-colors border border-indigo-100"
                    >
                        <Activity size={16} /> ✨ AI 自動尋找最佳參數
                    </button>
                </div>

                {/* Optimization Result Card */}
                {optResult && optResult.best && (
                    <Card className="bg-gradient-to-r from-indigo-50 to-blue-50 border-indigo-100 animate-in fade-in slide-in-from-top-2">
                        <CardContent className="p-4 flex flex-col md:flex-row items-center justify-between gap-4">
                            <div className="flex-1">
                                <h3 className="font-bold text-indigo-900 flex items-center gap-2">
                                    🏆 最佳策略發現 (ROI: {optResult.best.roi}%)
                                </h3>
                                <p className="text-sm text-indigo-700 mt-1">
                                    經過 {optResult.total_tested} 次組合測試，最佳參數為：
                                </p>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2 text-sm font-mono bg-white/60 p-2 rounded-md">
                                    <span>MA短: {optResult.best.params.MA_SHORT_DAYS}</span>
                                    <span>MA長: {optResult.best.params.MA_LONG_DAYS}</span>
                                    <span>RSI: {optResult.best.params.RSI_THRESHOLD}</span>
                                    <span>KD: {optResult.best.params.KD_THRESHOLD}</span>
                                </div>
                                <div className="text-xs text-indigo-500 mt-1 flex gap-3">
                                    <span>勝率: {optResult.best.win_rate}%</span>
                                    <span>總交易數: {optResult.best.trades}</span>
                                </div>
                            </div>
                            <button
                                onClick={() => handleRunBacktest(optResult.best.params)}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md shadow-sm text-sm font-bold whitespace-nowrap"
                            >
                                🚀 套用並回測
                            </button>
                        </CardContent>
                    </Card>
                )}
            </div>

            {/* Results */}
            {result && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <Card className={`border-0 shadow-md ${result.summary.total_return_pct >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
                            <CardContent className="p-6">
                                <div className="text-sm font-medium text-slate-500 flex items-center gap-2">
                                    <Activity size={16} /> 總報酬率 (ROI)
                                </div>
                                <div className={`text-3xl font-bold mt-2 ${result.summary.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {result.summary.total_return_pct > 0 ? '+' : ''}{result.summary.total_return_pct}%
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="border-0 shadow-md bg-white">
                            <CardContent className="p-6">
                                <div className="text-sm font-medium text-slate-500 flex items-center gap-2">
                                    <TrendingUp size={16} /> 勝率 (Win Rate)
                                </div>
                                <div className="text-3xl font-bold text-slate-800 mt-2">
                                    {result.summary.win_rate}%
                                </div>
                                <div className="text-xs text-slate-400 mt-1">
                                    {result.summary.win_count} 勝 {result.summary.loss_count} 敗
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="border-0 shadow-md bg-white">
                            <CardContent className="p-6">
                                <div className="text-sm font-medium text-slate-500 flex items-center gap-2">
                                    <DollarSign size={16} /> 最終權益 (Equity)
                                </div>
                                <div className="text-3xl font-bold text-slate-800 mt-2">
                                    ${result.summary.end_capital.toLocaleString()}
                                </div>
                                <div className="text-xs text-slate-400 mt-1">
                                    初始: ${result.summary.start_capital.toLocaleString()}
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="border-0 shadow-md bg-white">
                            <CardContent className="p-6">
                                <div className="text-sm font-medium text-slate-500 flex items-center gap-2">
                                    <TrendingDown size={16} /> 總交易次數
                                </div>
                                <div className="text-3xl font-bold text-slate-800 mt-2">
                                    {result.summary.total_trades}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Chart */}
                    <Card className="shadow-lg border-0 bg-white">
                        <CardHeader>
                            <CardTitle>📈 股價走勢與買賣點位</CardTitle>
                        </CardHeader>


                        <CardContent>
                            <div style={{ width: '100%', height: 400 }}>
                                <ResponsiveContainer>
                                    <ComposedChart data={result.daily_history}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                        <XAxis dataKey="date" tick={{ fontSize: 12 }} minTickGap={30} />
                                        <YAxis yAxisId="right" orientation="right" domain={['auto', 'auto']} />
                                        <Tooltip
                                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                        />
                                        <Legend />
                                        <Line
                                            yAxisId="right"
                                            type="monotone"
                                            dataKey="price"
                                            stroke="#2563eb"
                                            strokeWidth={2}
                                            dot={renderCustomizedDot}
                                            name="股價"
                                        />
                                        {/* Equity Curve could be added here on left axis if desired */}
                                    </ComposedChart>
                                </ResponsiveContainer>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Trade List */}
                    <Card className="shadow-md border-0 bg-white">
                        <CardHeader>
                            <CardTitle>📋 交易明細</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                    <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                                        <tr>
                                            <th className="px-4 py-3">日期</th>
                                            <th className="px-4 py-3">類型</th>
                                            <th className="px-4 py-3">價格</th>
                                            <th className="px-4 py-3">損益</th>
                                            <th className="px-4 py-3">訊號原因</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {result.trades.map((trade, idx) => (
                                            <tr key={idx} className="hover:bg-slate-50">
                                                <td className="px-4 py-3">{trade.date}</td>
                                                <td className={`px-4 py-3 font-bold ${trade.type.includes('BUY') ? 'text-green-600' : 'text-red-600'}`}>
                                                    {trade.type}
                                                </td>
                                                <td className="px-4 py-3 font-mono">{trade.price}</td>
                                                <td className={`px-4 py-3 font-mono ${trade.profit && trade.profit > 0 ? 'text-green-600' : (trade.profit && trade.profit < 0 ? 'text-red-600' : '')}`}>
                                                    {trade.profit ? `$${trade.profit} (${trade.profit_pct}%)` : '-'}
                                                </td>
                                                <td className="px-4 py-3 text-slate-500 text-xs max-w-xs truncate" title={trade.reason}>
                                                    {trade.reason}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </CardContent>
                    </Card>

                </div>
            )}
        </div>
    );
}
