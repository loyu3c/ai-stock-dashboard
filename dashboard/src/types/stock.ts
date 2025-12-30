export interface StockData {
    Stock: string;
    Date: string;
    Close: number;
    Signal: '🟢' | '🔴' | '🟡';
    Memo: string;
    K: number;
    D: number;
    RSI: number;
}
