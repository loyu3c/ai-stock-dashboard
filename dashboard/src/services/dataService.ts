import { api } from './api';
import type { StockData } from '../types/stock';

export const fetchStockData = async (): Promise<StockData[]> => {
    try {
        const data = await api.fetchAnalysisResults();

        if (!data) return [];

        // Map to StockData interface
        return data.map((item: any) => {
            // indicators is already an object from backend (or need parsing if raw string?)
            // Backend DBManager creates dict, FastAPI serializes to JSON.
            // But DBManager stores 'indicators' as JSON string in DB, 
            // and fetch_latest_analysis parses it to dict. 
            // So 'item.indicators' should be an object.

            const indicators = item.indicators || {};

            return {
                Stock: item.stock_code,
                Name: indicators.Name || '',
                Date: item.date,
                Signal: item.signal,
                Close: item.price,
                Memo: indicators.Memo || indicators.Signal_Memo || '',
                K: indicators.K || 0,
                D: indicators.D || 0,
                RSI: indicators.RSI || 0
            } as StockData;
        });

    } catch (err) {
        console.error("Fetching stock data failed:", err);
        return [];
    }
};
