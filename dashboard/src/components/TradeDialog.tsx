import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from './ui/dialog';
import { Tabs, TabsList, TabsTrigger } from './ui/tabs';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { api } from '../services/api';

interface TradeDialogProps {
    stockCode: string;
    stockName: string;
    currentPrice: number;
    isOpen: boolean;
    onClose: () => void;
    onOrderPlaced?: () => void;
    accountBalance?: number;
}

const TradeDialog: React.FC<TradeDialogProps> = ({
    stockCode,
    stockName,
    currentPrice,
    isOpen,
    onClose,
    onOrderPlaced,
    accountBalance
}) => {
    const [action, setAction] = useState<'BUY' | 'SELL'>('BUY');
    const [price, setPrice] = useState<number>(currentPrice);
    const [quantity, setQuantity] = useState<number>(1000);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Reset state when dialog opens
    useEffect(() => {
        if (isOpen) {
            setPrice(currentPrice);
            setQuantity(1000);
            setError(null);
            setAction('BUY');
        }
    }, [isOpen, currentPrice]);

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);
        try {
            await api.placeOrder({
                stock_code: stockCode,
                action: action,
                price: price,
                quantity: quantity
            });
            alert(`${action === 'BUY' ? '買進' : '賣出'} 委託已送出！`);
            onClose();
            if (onOrderPlaced) onOrderPlaced();
        } catch (err: any) {
            setError(err.message || "下單失敗");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Est. Cost Logic
    // Fee: 0.1425%, Tax: 0.3% (Sell Only)
    const subtotal = price * quantity;
    const fee = Math.floor(Math.max(20, subtotal * 0.001425));
    const tax = action === 'SELL' ? Math.floor(subtotal * 0.003) : 0;
    const total = action === 'BUY' ? subtotal + fee : subtotal - fee - tax;

    // Balance Check
    const isInsufficientBalance = action === 'BUY' && accountBalance !== undefined && total > accountBalance;

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{stockName} ({stockCode})</DialogTitle>
                    <DialogDescription>
                        目前價格: {currentPrice}
                        {accountBalance !== undefined && (
                            <span className="block mt-1 font-medium text-slate-600">
                                可用餘額: TWD {Math.floor(accountBalance).toLocaleString()}
                            </span>
                        )}
                    </DialogDescription>
                </DialogHeader>

                <Tabs value={action} onValueChange={(v) => setAction(v as 'BUY' | 'SELL')} className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="BUY" className="data-[state=active]:bg-red-500 data-[state=active]:text-white">買進 (Buy)</TabsTrigger>
                        <TabsTrigger value="SELL" className="data-[state=active]:bg-green-500 data-[state=active]:text-white">賣出 (Sell)</TabsTrigger>
                    </TabsList>

                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="price" className="text-right">
                                價格
                            </Label>
                            <Input
                                id="price"
                                type="number"
                                value={price}
                                onChange={(e) => setPrice(parseFloat(e.target.value))}
                                className="col-span-3"
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="quantity" className="text-right">
                                數量
                            </Label>
                            <Input
                                id="quantity"
                                type="number"
                                step="1000"
                                value={quantity}
                                onChange={(e) => setQuantity(parseInt(e.target.value))}
                                className="col-span-3"
                            />
                        </div>
                    </div>

                    <div className="bg-slate-50 p-4 rounded-lg space-y-2 mb-4">
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-500">小計</span>
                            <span>{Math.floor(subtotal).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-500">手續費 (~0.1425%)</span>
                            <span>{fee}</span>
                        </div>
                        {action === 'SELL' && (
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-500">證交稅 (0.3%)</span>
                                <span>{tax}</span>
                            </div>
                        )}
                        <div className="border-t border-slate-200 pt-2 flex justify-between font-bold">
                            <span>預估{action === 'BUY' ? '成本' : '收入'}</span>
                            <span className={action === 'BUY' ? 'text-red-600' : 'text-green-600'}>
                                {Math.floor(total).toLocaleString()} TWD
                            </span>
                        </div>

                        {isInsufficientBalance && (
                            <div className="text-red-600 text-sm font-bold text-right pt-1">
                                ⚠️ 餘額不足 (短缺 {Math.floor(total - (accountBalance || 0)).toLocaleString()})
                            </div>
                        )}
                    </div>
                </Tabs>

                {error && <div className="text-red-500 text-sm mb-2">{error}</div>}

                <DialogFooter>
                    <Button variant="outline" onClick={onClose}>取消</Button>
                    <Button
                        onClick={handleSubmit}
                        disabled={loading || isInsufficientBalance}
                        className={action === 'BUY' ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"}
                    >
                        {loading ? '送出中...' : `確認${action === 'BUY' ? '買進' : '賣出'}`}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};

export default TradeDialog;
