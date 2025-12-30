import Papa from 'papaparse';
import type { StockData } from '../types/stock';

// Placeholder URL - User needs to replace this
const SHEET_CSV_URL = import.meta.env.VITE_GOOGLE_SHEET_CSV_URL || "";

export const fetchStockData = async (): Promise<StockData[]> => {
    if (!SHEET_CSV_URL) {
        console.warn("Google Sheet CSV URL is not configured.");
        return [];
    }

    return new Promise((resolve, reject) => {
        Papa.parse(SHEET_CSV_URL, {
            download: true,
            header: true,
            dynamicTyping: true,
            complete: (results) => {
                if (results.data) {
                    // Filter out empty rows or malformed data
                    const validData = (results.data as StockData[]).filter(row => row.Stock && row.Signal);
                    resolve(validData);
                } else {
                    resolve([]);
                }
            },
            error: (error) => {
                reject(error);
            },
        });
    });
};
