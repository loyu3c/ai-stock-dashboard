import { supabase } from '../supabaseClient';
import type { StockData } from '../types/stock';

export const fetchStockData = async (): Promise<StockData[]> => {
    try {
        // Fetch latest analysis results
        // standard Postgres hack for "latest item per group": 
        // distinct on (stock_code) ... order by stock_code, date desc

        const { data, error } = await supabase
            .from('analysis_results')
            .select('*')
            .order('stock_code', { ascending: true })
            .order('date', { ascending: false });

        if (error) {
            console.error("Supabase fetch error:", error);
            throw error;
        }

        if (!data) return [];

        // Manual "Distinct On" filter if we don't assume the SQL distinct worked perfectly via API options
        // (Supabase JS client sometimes needs specific syntax for distinct, doing it in JS is safer for small datasets)
        const latestMap = new Map();
        data.forEach(item => {
            if (!latestMap.has(item.stock_code)) {
                latestMap.set(item.stock_code, item);
            }
        });

        const latestData = Array.from(latestMap.values());

        // Map to StockData interface
        return latestData.map(item => {
            // indicators is stored as JSONB, which comes back as an object
            const indicators = item.indicators || {};

            return {
                Stock: item.stock_code,
                Name: indicators.Name || '', // We stored Name in indicators
                Date: item.date,
                Signal: item.signal,
                Close: item.price,
                Memo: indicators.Memo || indicators.Signal_Memo || '', // Mapped to Memo
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
