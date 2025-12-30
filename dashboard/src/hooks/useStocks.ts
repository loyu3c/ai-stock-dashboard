import { useState, useEffect } from 'react';
import type { StockData } from '../types/stock';
import { fetchStockData } from '../services/dataService';

export const useStocks = () => {
    const [stocks, setStocks] = useState<StockData[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                const data = await fetchStockData();
                setStocks(data);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch data');
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    return { stocks, loading, error };
};
