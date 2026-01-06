import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { cn } from '../lib/utils';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

interface Transaction {
    id: number;
    stock_code: string;
    action: string;
    price: number;
    quantity: number;
    fee: number;
    tax: number;
    total_amount: number;
    date: string;
    memo: string;
}

interface TransactionTableProps {
    transactions: Transaction[];
    loading: boolean;
}

type SortKey = keyof Transaction;
type SortDirection = 'asc' | 'desc';

const TransactionTable: React.FC<TransactionTableProps> = ({ transactions, loading }) => {
    // Sorting State
    const [sortKey, setSortKey] = useState<SortKey>('date');
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

    const handleSort = (key: SortKey) => {
        if (sortKey === key) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortDirection('desc'); // Default desc for transactions mostly
        }
    };

    const getSortIcon = (key: SortKey) => {
        if (sortKey !== key) return <ArrowUpDown size={14} className="ml-1 text-slate-300" />;
        return sortDirection === 'asc'
            ? <ArrowUp size={14} className="ml-1 text-slate-600" />
            : <ArrowDown size={14} className="ml-1 text-slate-600" />;
    };

    if (loading) {
        return <div className="text-center p-10">載入交易紀錄中...</div>;
    }

    if (transactions.length === 0) {
        return <div className="text-center p-10 text-slate-500">尚無交易紀錄</div>;
    }

    // Sort Logic
    const sortedTransactions = [...transactions].sort((a, b) => {
        let valA = a[sortKey];
        let valB = b[sortKey];

        // Date sorting
        if (sortKey === 'date') {
            valA = new Date(valA as string).getTime();
            valB = new Date(valB as string).getTime();
        }

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
                <CardTitle className="text-slate-800">交易歷史紀錄</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                            <tr>
                                <SortableHeader label="日期" sKey="date" />
                                <SortableHeader label="代號" sKey="stock_code" />
                                <SortableHeader label="買賣" sKey="action" />
                                <SortableHeader label="價格" sKey="price" align="right" />
                                <SortableHeader label="數量" sKey="quantity" align="right" />
                                <SortableHeader label="手續費" sKey="fee" align="right" />
                                <SortableHeader label="證交稅" sKey="tax" align="right" />
                                <SortableHeader label="總金額" sKey="total_amount" align="right" />
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {sortedTransactions.map((tx) => (
                                <tr key={tx.id} className="bg-white hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap text-slate-500">
                                        {new Date(tx.date).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 font-bold text-slate-700">{tx.stock_code}</td>
                                    <td className="px-6 py-4">
                                        <span className={cn(
                                            "px-2 py-1 rounded text-xs font-medium",
                                            tx.action === 'BUY' ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
                                        )}>
                                            {tx.action === 'BUY' ? '買進' : '賣出'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono">{tx.price}</td>
                                    <td className="px-6 py-4 text-right font-mono">{tx.quantity}</td>
                                    <td className="px-6 py-4 text-right text-slate-500">{Math.floor(tx.fee)}</td>
                                    <td className="px-6 py-4 text-right text-slate-500">{Math.floor(tx.tax)}</td>
                                    <td className={cn(
                                        "px-6 py-4 text-right font-bold font-mono",
                                        tx.action === 'BUY' ? "text-red-600" : "text-green-600"
                                    )}>
                                        {Math.floor(tx.total_amount).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    );
};

export default TransactionTable;
