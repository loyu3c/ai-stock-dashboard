import { useState, useEffect } from 'react';
import { api } from '../services/api';
import TransactionTable from './TransactionTable';
import PositionTable from './PositionTable';
import AccountSwitcher from './AccountSwitcher';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Wallet, RefreshCcw } from 'lucide-react';
import { Button } from './ui/button';
import TradeDialog from './TradeDialog';

const TransactionPage = () => {
    const [transactions, setTransactions] = useState([]);
    const [accountStatus, setAccountStatus] = useState<any>(null);
    const [positions, setPositions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [stocks, setStocks] = useState<any[]>([]); // To get current prices

    // Trade Dialog state
    const [selectedStockCode, setSelectedStockCode] = useState<string | null>(null);
    const [isTradeOpen, setIsTradeOpen] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [statusRes, transRes, stockRes, configRes, optRes] = await Promise.all([
                api.fetchAccountStatus(),
                api.fetchTransactions(),
                api.fetchAnalysisResults(), // Current Price, Signal, Name
                api.fetchStockList(),       // Memo
                api.getOptimizerResults()   // Best Params
            ]);

            setAccountStatus(statusRes);
            setTransactions(transRes);
            setStocks(stockRes);

            // Create Lookups
            const stockMap = new Map(stockRes.map((s: any) => [s.Stock, s]));
            const configMap = new Map((configRes.stock_list || []).map((s: any) => [s.Stock, s]));
            const optMap = optRes || {}; // Keys are stock codes

            // Map positions with enriched data
            if (statusRes.positions) {
                const enrichedPositions = statusRes.positions.map((pos: any) => {
                    const stockInfo = stockMap.get(pos.stock_code);
                    const configInfo = configMap.get(pos.stock_code);
                    const optInfo = optMap[pos.stock_code];

                    const currentPrice = stockInfo ? (typeof stockInfo.Close === 'string' ? parseFloat(stockInfo.Close) : stockInfo.Close) : pos.avg_cost;

                    return {
                        ...pos,
                        stock_name: stockInfo?.Name || configInfo?.Name || '',
                        current_price: currentPrice,
                        signal: stockInfo?.Signal || '-',
                        memo: configInfo?.Memo || '',
                        best_params: optInfo?.best?.params || null
                    };
                });
                setPositions(enrichedPositions);
            } else {
                setPositions([]);
            }

        } catch (e) {
            console.error("Failed to fetch transaction data", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleTrade = (stockCode: string) => {
        setSelectedStockCode(stockCode);
        setIsTradeOpen(true);
    };

    // Find current price for dialog
    const getStockPrice = (code: string) => {
        const stock = stocks.find(s => s.Stock === code);
        return stock ? (typeof stock.Close === 'string' ? parseFloat(stock.Close) : stock.Close) : 0;
    };

    const getStockName = (code: string) => {
        const stock = stocks.find(s => s.Stock === code);
        return stock ? stock.Name : code;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">💰 資產與交易管理</h1>
                <div className="flex gap-4">
                    <Button variant="outline" onClick={fetchData} disabled={loading} className="flex items-center gap-2">
                        <RefreshCcw size={16} className={loading ? "animate-spin" : ""} /> 重新整理
                    </Button>
                    <AccountSwitcher onAccountChange={fetchData} />
                </div>
            </div>

            {/* Asset Summary */}
            {accountStatus && (
                <Card className="bg-slate-50 border-slate-200 shadow-sm">
                    <CardHeader className="pb-2 border-b border-slate-200">
                        <CardTitle className="text-slate-700 flex items-center gap-2">
                            <Wallet size={20} className="text-slate-500" /> 資產總覽
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            <div>
                                <div className="text-sm text-slate-500 font-bold uppercase tracking-wider mb-1">總資產 (Total Assets)</div>
                                <div className="text-3xl font-black text-slate-900 font-mono">
                                    TWD {Math.floor(accountStatus.balance + (positions.reduce((sum, p) => sum + (p.quantity * (p.current_price || 0)), 0))).toLocaleString()}
                                </div>
                            </div>
                            <div>
                                <div className="text-sm text-slate-500 font-bold uppercase tracking-wider mb-1">現金餘額 (Cash Balance)</div>
                                <div className="text-2xl font-bold text-slate-700 font-mono">
                                    TWD {Math.floor(accountStatus.balance).toLocaleString()}
                                </div>
                            </div>
                            <div>
                                <div className="text-sm text-slate-500 font-bold uppercase tracking-wider mb-1">證券市值 (Market Value)</div>
                                <div className="text-2xl font-bold text-slate-700 font-mono">
                                    TWD {Math.floor(positions.reduce((sum, p) => sum + (p.quantity * (p.current_price || 0)), 0)).toLocaleString()}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Positions */}
            <PositionTable
                positions={positions}
                loading={loading}
                onTrade={handleTrade}
                onMemoUpdate={fetchData}
            />

            {/* History */}
            <TransactionTable transactions={transactions} loading={loading} />

            {/* Trade Dialog */}
            {selectedStockCode && (
                <TradeDialog
                    stockCode={selectedStockCode}
                    stockName={getStockName(selectedStockCode)}
                    currentPrice={getStockPrice(selectedStockCode)}
                    isOpen={isTradeOpen}
                    onClose={() => setIsTradeOpen(false)}
                    onOrderPlaced={fetchData}
                    accountBalance={accountStatus?.balance}
                />
            )}
        </div>
    );
};

export default TransactionPage;
