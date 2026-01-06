// Force absolute URL to bypass potentially broken proxy/rewrite
const API_BASE_URL = "http://localhost:8000/api";

export const api = {
    // Stocks
    async fetchStockList() {
        const res = await fetch(`${API_BASE_URL}/config`);
        if (!res.ok) throw new Error("Failed to fetch config");
        return res.json();
    },

    async saveStockList(stocks: any[]) {
        const res = await fetch(`${API_BASE_URL}/save_stock_list`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(stocks),
        });
        if (!res.ok) throw new Error("Failed to save stocks");
        return res.json();
    },

    async saveStrategy(config: any) {
        const res = await fetch(`${API_BASE_URL}/save_strategy`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ config }),
        });
        if (!res.ok) throw new Error("Failed to save strategy");
        return res.json();
    },

    async addStock(stock: any) {
        const res = await fetch(`${API_BASE_URL}/add_stock`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(stock),
        });
        if (!res.ok) throw new Error("Failed to add stock");
        return res.json();
    },

    async fetchAnalysisResults() {
        const res = await fetch(`${API_BASE_URL}/analysis_results`);
        if (!res.ok) throw new Error("Failed to fetch analysis results");
        return res.json();
    },

    // Scanner
    async scanMarket(type: string, limit: number) {
        const res = await fetch(`${API_BASE_URL}/scan_market`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ type, limit }),
        });
        if (!res.ok) throw new Error("Failed to scan market");
        return res.json();
    },

    // Backtest
    async runBacktest(params: any) {
        const res = await fetch(`${API_BASE_URL}/run_backtest`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(params),
        });
        if (!res.ok) throw new Error("Failed to run backtest");
        return res.json();
    },

    // Optimize
    async optimizeStrategy(params: any) {
        const res = await fetch(`${API_BASE_URL}/optimize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(params),
        });
        if (!res.ok) throw new Error("Failed to optimize");
        return res.json();
    },

    // Optimizer Results
    async getOptimizerResults() {
        const res = await fetch(`${API_BASE_URL}/opt_results`);
        if (!res.ok) throw new Error("Failed to fetch optimizer results");
        return res.json();
    },

    // --- Account System ---
    async fetchAccounts() {
        const res = await fetch(`${API_BASE_URL}/accounts`);
        if (!res.ok) throw new Error("Failed to fetch accounts");
        return res.json();
    },

    async switchAccount(accountId: number) {
        const res = await fetch(`${API_BASE_URL}/accounts/switch`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ account_id: accountId }),
        });
        if (!res.ok) throw new Error("Failed to switch account");
        return res.json();
    },

    async fetchAccountStatus() {
        const res = await fetch(`${API_BASE_URL}/account/status`);
        if (!res.ok) throw new Error("Failed to fetch account status");
        return res.json();
    },

    async placeOrder(order: { stock_code: string; action: string; price: number; quantity: number }) {
        const res = await fetch(`${API_BASE_URL}/place_order`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(order),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to place order");
        }
        return res.json();
    },

    async fetchTransactions() {
        const res = await fetch(`${API_BASE_URL}/account/transactions`);
        if (!res.ok) throw new Error("Failed to fetch transactions");
        return res.json();
    }
};
