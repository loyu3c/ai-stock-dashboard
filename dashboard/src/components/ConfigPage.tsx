import { useState, useEffect } from 'react';
import { Save, Plus, Trash2, RefreshCw, Info } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';

interface StockItem {
    Stock: string;
    Name: string;
    Enabled: string | boolean;
    Memo: string;
}

interface StrategyConfig {
    [key: string]: number | string;
}

const API_BASE = 'http://localhost:8000/api';

const ConfigPage = () => {
    const [loading, setLoading] = useState(true);
    const [stockList, setStockList] = useState<StockItem[]>([]);
    const [strategy, setStrategy] = useState<StrategyConfig>({});
    const [activeSection, setActiveSection] = useState<'stocks' | 'strategy'>('stocks');
    const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

    useEffect(() => {
        fetchConfig();
    }, []);

    const fetchConfig = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/config`);
            if (!res.ok) throw new Error("Failed to connect to local server");
            const data = await res.json();
            setStockList(data.stock_list);
            setStrategy(data.strategy);
            setMessage(null);
        } catch (err) {
            console.error(err);
            setMessage({ text: "無法連接到後端伺服器 (請確認是否執行 python server.py)", type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleSaveStocks = async () => {
        try {
            // Ensure Enabled is string "TRUE"/"FALSE" for consistency with Python backend expectation if needed
            // Or backend handles it. Python expectation: Pydantic 'Enabled: str'.
            // Let's convert boolean to "TRUE"/"FALSE" just in case or keep consistency using what we got.
            // The sheet has "TRUE".

            const payload = stockList.map(s => ({
                ...s,
                Enabled: s.Enabled === true || s.Enabled === "TRUE" ? "TRUE" : "FALSE"
            }));

            const res = await fetch(`${API_BASE}/save_stock_list`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error("Save failed");
            setMessage({ text: "自選股清單已儲存！", type: 'success' });
        } catch (err) {
            setMessage({ text: "儲存失敗", type: 'error' });
        }
    };

    const handleSaveStrategy = async () => {
        try {
            const res = await fetch(`${API_BASE}/save_strategy`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ config: strategy })
            });
            if (!res.ok) throw new Error("Save failed");
            setMessage({ text: "策略參數已儲存！", type: 'success' });
        } catch (err) {
            setMessage({ text: "儲存失敗", type: 'error' });
        }
    };

    const addStock = () => {
        setStockList([...stockList, { Stock: "", Name: "", Enabled: "TRUE", Memo: "" }]);
    };

    const removeStock = (index: number) => {
        const newList = [...stockList];
        newList.splice(index, 1);
        setStockList(newList);
    };

    const updateStock = (index: number, field: keyof StockItem, value: any) => {
        const newList = [...stockList];
        newList[index] = { ...newList[index], [field]: value };
        setStockList(newList);
    };

    if (loading) return <div className="p-10 text-center">載入設定中...</div>;

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            <h1 className="text-3xl font-extrabold mb-8 text-slate-800 tracking-tight">⚙️ 系統設定</h1>

            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-6 flex items-start gap-3">
                <Info className="text-blue-600 mt-1 shrink-0" size={20} />
                <div className="text-sm text-blue-800">
                    <p className="font-semibold mb-1">關於存檔功能：</p>
                    <ul className="list-disc pl-4 space-y-1 text-blue-700">
                        <li>此處的修改會直接同步至您的 <strong>Google 試算表</strong>。</li>
                        <li>為了確保功能正常，請務必在電腦上持續執行後端程式：<code>python server.py</code></li>
                        <li>按下「儲存」後，若看到綠色成功訊息，即代表雲端試算表已更新。</li>
                    </ul>
                </div>
            </div>

            {message && (
                <div className={`p-4 rounded ${message.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {message.text}
                </div>
            )}

            <div className="flex space-x-4 mb-6">
                <button
                    onClick={() => setActiveSection('stocks')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeSection === 'stocks' ? 'bg-slate-800 text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}
                >
                    自選股清單
                </button>
                <button
                    onClick={() => setActiveSection('strategy')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeSection === 'strategy' ? 'bg-slate-800 text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}
                >
                    策略參數
                </button>
                <button onClick={fetchConfig} className="ml-auto p-2 text-slate-400 hover:text-slate-600" title="重新整理">
                    <RefreshCw size={20} />
                </button>
            </div>

            {activeSection === 'stocks' && (
                <Card className="border-slate-100 shadow-sm">
                    <CardHeader className="flex flex-row items-center justify-between border-b border-slate-100 bg-white">
                        <CardTitle className="text-slate-800">管理自選股</CardTitle>
                        <button onClick={addStock} className="flex items-center gap-1 text-sm bg-blue-50 text-blue-600 px-3 py-1 rounded hover:bg-blue-100">
                            <Plus size={16} /> 新增
                        </button>
                    </CardHeader>
                    <CardContent className="p-0">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                                    <tr>
                                        <th className="px-6 py-3">啟用</th>
                                        <th className="px-6 py-3">代號</th>
                                        <th className="px-6 py-3">名稱</th>
                                        <th className="px-6 py-3">備註</th>
                                        <th className="px-6 py-3">操作</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {stockList.map((stock, idx) => (
                                        <tr key={idx} className="bg-white hover:bg-slate-50">
                                            <td className="px-6 py-3">
                                                <input
                                                    type="checkbox"
                                                    checked={stock.Enabled === "TRUE" || stock.Enabled === true}
                                                    onChange={(e) => updateStock(idx, 'Enabled', e.target.checked ? "TRUE" : "FALSE")}
                                                    className="rounded border-gray-300"
                                                />
                                            </td>
                                            <td className="px-6 py-3">
                                                <input
                                                    value={stock.Stock}
                                                    onChange={(e) => updateStock(idx, 'Stock', e.target.value)}
                                                    className="w-20 p-1 border rounded"
                                                    placeholder="2330"
                                                />
                                            </td>
                                            <td className="px-6 py-3">
                                                <input
                                                    value={stock.Name}
                                                    onChange={(e) => updateStock(idx, 'Name', e.target.value)}
                                                    className="w-24 p-1 border rounded"
                                                    placeholder="台積電"
                                                />
                                            </td>
                                            <td className="px-6 py-3">
                                                <input
                                                    value={stock.Memo}
                                                    onChange={(e) => updateStock(idx, 'Memo', e.target.value)}
                                                    className="w-full p-1 border rounded"
                                                    placeholder="備註..."
                                                />
                                            </td>
                                            <td className="px-6 py-3 text-red-500 cursor-pointer hover:text-red-700" onClick={() => removeStock(idx)}>
                                                <Trash2 size={16} />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
                            <button onClick={handleSaveStocks} className="flex items-center gap-2 bg-slate-800 text-white px-4 py-2 rounded hover:bg-slate-700">
                                <Save size={16} /> 儲存變更
                            </button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {activeSection === 'strategy' && (
                <Card className="border-slate-100 shadow-sm">
                    <CardHeader className="border-b border-slate-100 bg-white">
                        <CardTitle className="text-slate-800">策略參數設定</CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 bg-white">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {Object.entries(strategy).map(([key, val]) => (
                                <div key={key} className="space-y-2">
                                    <label className="text-sm font-medium text-slate-700">{key}</label>
                                    <input
                                        type="number"
                                        value={val}
                                        onChange={(e) => setStrategy({ ...strategy, [key]: Number(e.target.value) })}
                                        className="w-full p-2 border rounded focus:ring-2 focus:ring-slate-200 outline-none"
                                    />
                                    <p className="text-xs text-slate-400">
                                        {key.includes('MA') ? 'Moving Average Days' : key.includes('RSI') ? 'RSI Threshold' : 'Parameter'}
                                    </p>
                                </div>
                            ))}
                        </div>
                        <div className="mt-8 pt-6 border-t border-slate-100 flex justify-end">
                            <button onClick={handleSaveStrategy} className="flex items-center gap-2 bg-slate-800 text-white px-4 py-2 rounded hover:bg-slate-700">
                                <Save size={16} /> 儲存設定
                            </button>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default ConfigPage;
