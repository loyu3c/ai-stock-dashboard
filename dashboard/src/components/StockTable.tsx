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
        <Card className="w-full">
            <CardHeader>
                <CardTitle>每日選股清單</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                            <tr>
                                <th className="px-6 py-3">代號</th>
                                <th className="px-6 py-3">日期</th>
                                <th className="px-6 py-3">信號</th>
                                <th className="px-6 py-3">收盤價</th>
                                <th className="px-6 py-3">技術指標 (K/D/RSI)</th>
                                <th className="px-6 py-3">備註</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((stock) => (
                                <tr
                                    key={stock.Stock}
                                    className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                                >
                                    <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                                        {stock.Stock}
                                    </td>
                                    <td className="px-6 py-4">{stock.Date}</td>
                                    <td className="px-6 py-4 text-xl">{stock.Signal}</td>
                                    <td className="px-6 py-4 font-bold">{stock.Close}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex space-x-2">
                                            <span className={cn("px-2 py-1 rounded", stock.K < 30 ? "bg-green-100 text-green-800" : "bg-gray-100")}>K:{stock.K}</span>
                                            <span className="px-2 py-1 rounded bg-gray-100">D:{stock.D}</span>
                                            <span className={cn("px-2 py-1 rounded", stock.RSI > 80 ? "bg-red-100 text-red-800" : "bg-gray-100")}>RSI:{stock.RSI}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-gray-500">{stock.Memo}</td>
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
