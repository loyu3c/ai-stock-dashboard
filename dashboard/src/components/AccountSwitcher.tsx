import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

interface Account {
    id: number;
    name: string;
    type: string;
    balance: number;
}

interface Props {
    onAccountChange?: () => void;
}

const AccountSwitcher: React.FC<Props> = ({ onAccountChange }) => {
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [currentId, setCurrentId] = useState<number | null>(null);

    useEffect(() => {
        loadAccounts();
    }, []);

    const loadAccounts = async () => {
        try {
            const list = await api.fetchAccounts();
            setAccounts(list);

            const status = await api.fetchAccountStatus();
            setCurrentId(status.id);
        } catch (e) {
            console.error("Failed to load accounts", e);
        }
    };

    const handleSwitch = async (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newId = parseInt(e.target.value);
        try {
            await api.switchAccount(newId);
            setCurrentId(newId);
            if (onAccountChange) onAccountChange();
        } catch (error) {
            alert("Failed to switch account");
        }
    };

    if (!currentId) return <span>Loading...</span>;

    return (
        <div className="flex items-center space-x-2 bg-white p-2 rounded-lg shadow-sm border border-slate-200">
            <span className="text-sm font-medium text-slate-600">
                👤 帳戶:
            </span>
            <select
                value={currentId}
                onChange={handleSwitch}
                className="text-sm bg-slate-50 border-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1 outline-none font-bold text-slate-800"
            >
                {accounts.map(acc => (
                    <option key={acc.id} value={acc.id}>
                        {acc.name} ({acc.type === 'VIRTUAL' ? '模擬' : '正式'})
                    </option>
                ))}
            </select>
            {accounts.find(a => a.id === currentId)?.type === 'VIRTUAL' && (
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                    Virtual
                </span>
            )}
            {accounts.find(a => a.id === currentId)?.type === 'REAL' && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">
                    Real
                </span>
            )}
        </div>
    );
};

export default AccountSwitcher;
