import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { cn } from '../lib/utils';
import { Button } from './ui/button';
import { ReceiptText, Edit2, Check, X, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { api } from '../services/api';

interface Position {
    stock_code: string;
    quantity: number;
    avg_cost: number;
    current_price?: number;
    stock_name?: string;
    signal?: string;
    memo?: string;
    best_params?: any;
    market_value?: number;
    unrealized_pl?: number;
    return_rate?: number;
}

interface PositionTableProps {
    positions: Position[];
    loading: boolean;
    onTrade?: (stockCode: string) => void;
    onMemoUpdate?: () => void;
}

type SortKey = keyof Position | 'stock_name' | 'market_value' | 'unrealized_pl' | 'return_rate';
type SortDirection = 'asc' | 'desc';

const PositionTable: React.FC<PositionTableProps> = ({ positions, loading, onTrade, onMemoUpdate }) => {
    // Editing State
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editValue, setEditValue] = useState("");

    // Sorting State
    const [sortKey, setSortKey] = useState<SortKey>('stock_code');
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

    const handleSort = (key: SortKey) => {
        if (sortKey === key) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortDirection('asc');
        }
    };

    const getSortIcon = (key: SortKey) => {
        if (sortKey !== key) return <ArrowUpDown size={14} className="ml-1 text-slate-300" />;
        return sortDirection === 'asc'
            ? <ArrowUp size={14} className="ml-1 text-slate-600" />
            : <ArrowDown size={14} className="ml-1 text-slate-600" />;
    };

    const handleStartEdit = (stockCode: string, currentMemo: string) => {
        setEditingId(stockCode);
        setEditValue(currentMemo);
    };

    const handleSaveMemo = async (stockCode: string) => {
        try {
            await api.updateStockMemo(stockCode, editValue);
            setEditingId(null);
            if (onMemoUpdate) onMemoUpdate();
        } catch (e) {
            alert("更新備註失敗");
        }
    };

    const handleCancelEdit = () => {
        setEditingId(null);
    };

    if (loading) {
        return <div className="text-center p-10">載入持倉資料中...</div>;
    }

    if (positions.length === 0) {
        return <div className="text-center p-10 text-slate-500">目前無持倉</div>;
    }

    // Sort Logic
    // Pre-calculate derived values for sorting safely
    const sortedPositions = [...positions].sort((a, b) => {
        // Calculate derived values for comparison
        const getMarketValue = (p: Position) => p.market_value || (p.quantity * (p.current_price || p.avg_cost));
        const getCostBasis = (p: Position) => p.quantity * p.avg_cost;
        const getPL = (p: Position) => p.unrealized_pl || (getMarketValue(p) - getCostBasis(p));
        const getReturnRate = (p: Position) => getCostBasis(p) > 0 ? (getPL(p) / getCostBasis(p)) * 100 : 0;

        let valA: any = a[sortKey as keyof Position];
        let valB: any = b[sortKey as keyof Position];

        // Override for derived columns
        if (sortKey === 'market_value') {
            valA = getMarketValue(a);
            valB = getMarketValue(b);
        } else if (sortKey === 'unrealized_pl') {
            valA = getPL(a);
            valB = getPL(b);
        } else if (sortKey === 'return_rate') {
            valA = getReturnRate(a);
            valB = getReturnRate(b);
        }

        // Handle undefined/null (push to bottom usually, or treat as 0/empty)
        if (valA === undefined || valA === null) valA = (typeof valB === 'number' ? -Infinity : '');
        if (valB === undefined || valB === null) valB = (typeof valA === 'number' ? -Infinity : '');

        if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
        if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
        return 0;
    });

    const SortableHeader = ({ label, sKey, align = 'left' }: { label: string, sKey: SortKey, align?: 'left' | 'center' | 'right' }) => (
        <th
            className={`px-6 py-4 cursor-pointer hover:bg-slate-100 transition-colors ${align === 'right' ? 'text-right' : align === 'center' ? 'text-center' : 'text-left'}`}
            onClick={() => handleSort(sKey)}
        >
            <div className={`flex items-center ${align === 'right' ? 'justify-end' : align === 'center' ? 'justify-center' : 'justify-start'}`}>
                {label} {getSortIcon(sKey)}
            </div>
        </th>
    );

    return (
        <Card className="w-full border-slate-100 shadow-sm mt-4">
            <CardHeader className="border-b border-slate-100 bg-white">
                <CardTitle className="text-slate-800">目前持倉</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                            <tr>
                                <SortableHeader label="代號" sKey="stock_code" />
                                <SortableHeader label="名稱" sKey="stock_name" />
                                <SortableHeader label="數量" sKey="quantity" align="right" />
                                <SortableHeader label="成本" sKey="avg_cost" align="right" />
                                <SortableHeader label="現價" sKey="current_price" align="right" />
                                <SortableHeader label="損益" sKey="unrealized_pl" align="right" />
                                <SortableHeader label="報酬率" sKey="return_rate" align="right" />
                                <SortableHeader label="訊號" sKey="signal" align="center" />
                                <th className="px-6 py-4">最佳參數</th>
                                <SortableHeader label="備註" sKey="memo" />
                                <th className="px-6 py-4 text-center">操作</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {sortedPositions.map((pos) => {
                                const marketValue = pos.market_value || (pos.quantity * (pos.current_price || pos.avg_cost));
                                const costBasis = pos.quantity * pos.avg_cost;
                                const pl = pos.unrealized_pl || (marketValue - costBasis);
                                const plPercent = costBasis > 0 ? (pl / costBasis) * 100 : 0;
                                const isProfit = pl >= 0;

                                // Format Params
                                let paramsStr = "-";
                                if (pos.best_params) {
                                    const p = pos.best_params;
                                    const ma = `${p.MA_SHORT_DAYS || p.ma_short}/${p.MA_LONG_DAYS || p.ma_long}`;
                                    const rsi = `RSI:${p.RSI_THRESHOLD || p.rsi_threshold}`;
                                    const kd = `KD:${p.KD_THRESHOLD || p.kd_threshold}`;
                                    paramsStr = `${ma} ${rsi} ${kd}`;
                                }

                                return (
                                    <tr key={pos.stock_code} className="bg-white hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 font-bold text-slate-700">{pos.stock_code}</td>
                                        <td className="px-6 py-4 text-slate-600">{pos.stock_name || '-'}</td>
                                        <td className="px-6 py-4 text-right font-mono">{pos.quantity.toLocaleString()}</td>
                                        <td className="px-6 py-4 text-right font-mono">{Math.floor(pos.avg_cost).toLocaleString()}</td>
                                        <td className="px-6 py-4 text-right font-mono text-slate-500">
                                            {pos.current_price ? Math.floor(pos.current_price).toLocaleString() : '-'}
                                        </td>
                                        <td className={cn(
                                            "px-6 py-4 text-right font-bold font-mono",
                                            isProfit ? "text-red-600" : "text-green-600"
                                        )}>
                                            {Math.floor(pl).toLocaleString()}
                                        </td>
                                        <td className={cn(
                                            "px-6 py-4 text-right font-bold font-mono",
                                            isProfit ? "text-red-600" : "text-green-600"
                                        )}>
                                            {plPercent.toFixed(2)}%
                                        </td>
                                        <td className="px-6 py-4 text-center text-lg">{pos.signal || '-'}</td>
                                        <td className="px-6 py-4 text-xs font-mono text-slate-500">{paramsStr}</td>
                                        <td className="px-6 py-4 text-sm text-slate-500 min-w-[200px]">
                                            {editingId === pos.stock_code ? (
                                                <div className="flex items-center gap-1">
                                                    <input
                                                        className="border rounded px-2 py-1 w-full text-xs"
                                                        value={editValue}
                                                        onChange={(e) => setEditValue(e.target.value)}
                                                        autoFocus
                                                    />
                                                    <button onClick={() => handleSaveMemo(pos.stock_code)} className="text-green-600 hover:text-green-700 p-1"><Check size={14} /></button>
                                                    <button onClick={handleCancelEdit} className="text-red-400 hover:text-red-500 p-1"><X size={14} /></button>
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-2 group cursor-pointer hover:bg-slate-100 p-1 rounded" onClick={() => handleStartEdit(pos.stock_code, pos.memo || '')}>
                                                    <span className="truncate max-w-[150px]">{pos.memo || '(點擊新增備註)'}</span>
                                                    <Edit2 size={12} className="opacity-0 group-hover:opacity-50 text-slate-400" />
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="bg-blue-50 text-blue-600 border-blue-100 hover:bg-blue-100"
                                                onClick={() => onTrade && onTrade(pos.stock_code)}
                                            >
                                                <ReceiptText size={14} className="mr-1" /> 下單
                                            </Button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    );
};

export default PositionTable;
