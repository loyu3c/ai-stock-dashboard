import { useState } from 'react';
import type { StockData } from '../types/stock';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { cn } from '../lib/utils';
import { ArrowUpDown, ReceiptText } from 'lucide-react';
import { Button } from './ui/button';
import TradeDialog from './TradeDialog';

interface StockTableProps {
    data: StockData[];
    loading: boolean;
    accountBalance?: number;
}

const StockTable: React.FC<StockTableProps> = ({ data, loading, accountBalance }) => {
    const [sortConfig, setSortConfig] = useState<{ key: keyof StockData | null; direction: 'asc' | 'desc' }>({
        key: null,
        direction: 'asc',
    });
    const [selectedStock, setSelectedStock] = useState<StockData | null>(null);
    const [isTradeOpen, setIsTradeOpen] = useState(false);

    const handleTradeClick = (stock: StockData) => {
        setSelectedStock(stock);
        setIsTradeOpen(true);
    };

    const sortedData = [...data].sort((a, b) => {
        if (!sortConfig.key) return 0;

        const key = sortConfig.key;
        if (a[key] < b[key]) {
            return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (a[key] > b[key]) {
            return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
    });

    const handleSort = (key: keyof StockData) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    if (loading) {
        return <div className="text-center p-10">載入中...</div>;
    }

    if (data.length === 0) {
        return <div className="text-center p-10">目前沒有資料，或無法讀取 Google Sheet。</div>;
    }

    const renderSortHeader = (label: string, key: keyof StockData) => (
        <th
            className="px-6 py-4 font-semibold cursor-pointer hover:bg-slate-100 transition-colors select-none"
            onClick={() => handleSort(key)}
        >
            <div className="flex items-center gap-1">
                {label}
                <ArrowUpDown size={14} className="text-slate-400" />
            </div>
        </th>
    );

    return (
        <>
            <Card className="w-full border-slate-100 shadow-sm">
                <CardHeader className="border-b border-slate-100 bg-white">
                    <CardTitle className="text-slate-800">每日選股清單</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                                <tr>
                                    {renderSortHeader("代號", "Stock")}
                                    {renderSortHeader("名稱", "Name")}
                                    {renderSortHeader("日期", "Date")}
                                    {renderSortHeader("信號", "Signal")}
                                    {renderSortHeader("收盤價", "Close")}
                                    {renderSortHeader("技術指標 (K)", "K")}
                                    <th className="px-6 py-4 font-semibold">備註</th>
                                    <th className="px-6 py-4 font-semibold">操作</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {sortedData.map((stock) => (
                                    <tr
                                        key={stock.Stock}
                                        className="bg-white hover:bg-slate-50 transition-colors"
                                    >
                                        <td className="px-6 py-4 font-bold text-slate-700 whitespace-nowrap">
                                            {stock.Stock}
                                        </td>
                                        <td className="px-6 py-4 text-slate-600 font-medium">
                                            {stock.Name}
                                        </td>
                                        <td className="px-6 py-4 text-slate-600">{stock.Date}</td>
                                        <td className="px-6 py-4 text-xl">{stock.Signal}</td>
                                        <td className="px-6 py-4 font-mono font-bold text-slate-800">{stock.Close}</td>
                                        <td className="px-6 py-4">
                                            <div className="flex space-x-2">
                                                <span className={cn("px-2 py-1 rounded text-xs font-medium", stock.K < 30 ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-600")}>K:{stock.K}</span>
                                                <span className="px-2 py-1 rounded bg-slate-100 text-slate-600 text-xs font-medium">D:{stock.D}</span>
                                                <span className={cn("px-2 py-1 rounded text-xs font-medium", stock.RSI > 80 ? "bg-red-100 text-red-700" : "bg-slate-100 text-slate-600")}>RSI:{stock.RSI}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-slate-400">{stock.Memo}</td>
                                        <td className="px-6 py-4">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="bg-blue-50 text-blue-600 border-blue-100 hover:bg-blue-100"
                                                onClick={() => handleTradeClick(stock)}
                                            >
                                                <ReceiptText size={16} className="mr-1" /> 下單
                                            </Button>
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
                    stockCode={selectedStock.Stock.toString()}
                    stockName={selectedStock.Name}
                    currentPrice={typeof selectedStock.Close === 'number' ? selectedStock.Close : parseFloat(selectedStock.Close)}
                    isOpen={isTradeOpen}
                    onClose={() => setIsTradeOpen(false)}
                    accountBalance={accountBalance}
                />
            )}
        </>
    );
};

export default StockTable;
