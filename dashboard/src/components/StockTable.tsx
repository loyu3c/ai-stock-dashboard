import type { StockData } from '../types/stock';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { cn } from '../lib/utils';

interface StockTableProps {
    data: StockData[];
    loading: boolean;
}

const StockTable: React.FC<StockTableProps> = ({ data, loading }) => {
    if (loading) {
        return <div className="text-center p-10">載入中...</div>;
    }

    if (data.length === 0) {
        return <div className="text-center p-10">目前沒有資料，或無法讀取 Google Sheet。</div>;
    }

    return (
        <Card className="w-full border-slate-100 shadow-sm">
            <CardHeader className="border-b border-slate-100 bg-white">
                <CardTitle className="text-slate-800">每日選股清單</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                            <tr>
                                <th className="px-6 py-4 font-semibold">代號</th>
                                <th className="px-6 py-4 font-semibold">名稱</th>
                                <th className="px-6 py-4 font-semibold">日期</th>
                                <th className="px-6 py-4 font-semibold">信號</th>
                                <th className="px-6 py-4 font-semibold">收盤價</th>
                                <th className="px-6 py-4 font-semibold">技術指標 (K/D/RSI)</th>
                                <th className="px-6 py-4 font-semibold">備註</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {data.map((stock) => (
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
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    );
};

export default StockTable;
