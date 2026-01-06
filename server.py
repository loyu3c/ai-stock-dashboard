from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from db_manager import DBManager
import uvicorn
import logging

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

db_manager = DBManager() # Replaced supabase_manager

from account_manager import AccountManager
account_manager = AccountManager()
# Global state for current active account (Default to first found or None)
CURRENT_ACCOUNT_ID = 1 # Default to 1 (Virtual) usually


from typing import Union, Optional

# Data Models
class StockItem(BaseModel):
    Stock: Union[str, int, float]
    Name: Optional[str] = ""
    Enabled: Union[str, bool]
    Memo: Optional[str] = ""

class StrategyConfig(BaseModel):
    config: dict

@app.get("/api/config")
def get_config():
    """Fetches current stock list and strategy config."""
    try:
        # Fetch raw records including disabled ones
        raw_stocks = db_manager.fetch_all_stocks()
        
        # Strategy
        strategy = db_manager.fetch_strategy_config_full()
        
        return {
            "stock_list": raw_stocks,
            "strategy": strategy
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis_results")
def get_analysis_results():
    """Fetches latest analysis results for dashboard."""
    try:
        results = db_manager.fetch_latest_analysis()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/save_stock_list")
def save_stock_list(items: list[StockItem]):
    """Saves the full stock list."""
    # Convert Pydantic models to clean dicts
    data = []
    for item in items:
        row = item.dict()
        # SupabaseManager expects keys: Stock, Name, Enabled, Memo
        # It handles conversion of Enabled
        data.append(row)

    success = db_manager.save_stock_list(data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save stock list")
    return {"status": "success"}

@app.post("/api/save_strategy")
def save_strategy(data: StrategyConfig):
    """Saves strategy configuration."""
    success = db_manager.save_strategy_config(data.config)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save strategy")
    return {"status": "success"}

class MemoUpdate(BaseModel):
    stock_code: str
    memo: str

@app.post("/api/update_stock_memo")
def update_stock_memo_endpoint(data: MemoUpdate):
    """Updates memo for a specific stock."""
    success = db_manager.update_stock_memo(data.stock_code, data.memo)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update memo")
    return {"status": "success"}


# --- Market Scanner Endpoints ---

from market_scanner import MarketScanner

class ScanRequest(BaseModel):
    type: str = "volume_rank"
    limit: int = 20

@app.post("/api/scan_market")
async def scan_market(req: ScanRequest):
    print(f"⚡ Received Scan Request: {req.type} (Limit: {req.limit})")
    try:
        # Initialize Scanner (reuses Shioaji session)
        scanner = MarketScanner()
        
        # 1. Get Candidates
        candidates = scanner.get_market_candidates(scan_type=req.type, limit=req.limit)
        print(f"📋 Found {len(candidates)} candidates.")
        
        if not candidates:
            return []
            
        # 2. Run Analysis
        # Note: This takes time (e.g. 10s for 20 stocks). 
        df = scanner.run_scan(target_list=candidates)
        
        # 3. Return Results
        # Handle NaN values for JSON output
        df = df.fillna("")
        return df.to_dict(orient='records')
        
    except Exception as e:
        print(f"❌ Scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/add_stock")
async def add_stock(item: StockItem):
    """
    Adds a single stock to the watchlist.
    """
    try:
        # 1. Fetch current list
        current_list = db_manager.fetch_all_stocks()
        
        # 2. Check if exists
        stock_str = str(item.Stock).strip()
        for stock in current_list:
            if str(stock['Stock']).strip() == stock_str:
                return {"status": "skipped", "message": "Stock already exists"}
        
        # 3. Append
        new_entry = item.dict()
        # Ensure proper types for Supabase if needed (though SupabaseManager handles list)
        current_list.append(new_entry)
        
        # 4. Save
        if db_manager.save_stock_list(current_list):
            return {"status": "success", "message": f"Added {item.Stock}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save to Supabase")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Backtest Endpoints ---

from backtest_engine import BacktestEngine

class BacktestRequest(BaseModel):
    stock: str
    start_date: str
    end_date: str
    initial_capital: Optional[int] = 100000
    strategy_override: Optional[dict] = None

@app.post("/api/run_backtest")
async def run_backtest(req: BacktestRequest):
    print(f"📉 Running backtest for {req.stock} ({req.start_date} to {req.end_date})")
    try:
        # Determine strategy: Override > DB > Default
        if req.strategy_override:
             print(f"⚙️ Using Strategy Override: {req.strategy_override}")
             strategy_config = req.strategy_override
        else:
             strategy_config = db_manager.fetch_strategy_config()
        
        engine = BacktestEngine(initial_capital=req.initial_capital)
        result = await run_in_threadpool(engine.run, req.stock, req.start_date, req.end_date, strategy_config)
        
        if "error" in result:
             raise HTTPException(status_code=404, detail=result["error"])
             
        return result
            
    except Exception as e:
        print(f"❌ Backtest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Optimizer Endpoints ---
from optimizer import StrategyOptimizer

from datetime import datetime
import json
import os

# Persistence File
OPT_RESULTS_FILE = "data/optimization_results.json"

def load_opt_results():
    if os.path.exists(OPT_RESULTS_FILE):
        try:
            with open(OPT_RESULTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_opt_result(stock_code, result_data):
    data = load_opt_results()
    data[stock_code] = result_data
    with open(OPT_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class OptimizeRequest(BaseModel):
    stock: str
    start_date: str
    end_date: str


@app.post("/api/optimize")
async def optimize_strategy(req: OptimizeRequest):
    print(f"🧪 Starting optimization for {req.stock}...")
    try:
        opt = StrategyOptimizer()
        # Run optimization (This might take a while, 5-10s)
        # In production, use background tasks. Here, sync wait is acceptable for local tool.
        result = opt.optimize(req.stock, req.start_date, req.end_date)
        
        return result
            
    except Exception as e:
        print(f"❌ Optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse
import json
import asyncio

@app.post("/api/optimize_stream")
async def optimize_stream(req: OptimizeRequest):
    print(f"🌊 Streaming optimization for {req.stock}...")
    
    async def event_generator():
        opt = StrategyOptimizer()
        # The optimizer is synchronous but fast enough per step.
        # Use asyncio.to_thread to run the generator if it blocks too much, but here yielding is fine.
        # Since optimize_stream is a generator, we iterate it.
        
        for event in opt.optimize_stream(req.stock, req.start_date, req.end_date):
            if event['status'] == 'done' and event['result']:
                # Save result persistently
                res = event['result']
                # Add metadata
                res['last_run'] = datetime.now().isoformat()
                res['date_range'] = f"{req.start_date} ~ {req.end_date}"
                save_opt_result(req.stock, res)
                
                # Re-inject metadata into event for frontend immediate update
                event['result']['last_run'] = res['last_run']
                event['result']['date_range'] = res['date_range']

            yield json.dumps(event) + "\n"
            await asyncio.sleep(0.01) # Yield to event loop

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/api/opt_results")
async def get_opt_results():
    return load_opt_results()

# --- Account System Endpoints ---

class OrderRequest(BaseModel):
    stock_code: str
    action: str # BUY / SELL
    price: float
    quantity: int
    order_type: Optional[str] = "ROD"
    price_type: Optional[str] = "LMT"

class AccountSwitchRequest(BaseModel):
    account_id: int

@app.get("/api/accounts")
def get_accounts():
    """Get all available accounts."""
    return account_manager.get_all_accounts()

@app.get("/api/account/current")
def get_current_account_id():
    return {"account_id": CURRENT_ACCOUNT_ID}

@app.post("/api/accounts/switch")
def switch_account(req: AccountSwitchRequest):
    global CURRENT_ACCOUNT_ID
    # Validate exist
    acct = account_manager.get_account(req.account_id)
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")
    
    CURRENT_ACCOUNT_ID = req.account_id
    print(f"🔄 Switched to Account ID: {CURRENT_ACCOUNT_ID} ({acct.name})")
    return {"status": "success", "current_account": acct.name, "type": "VIRTUAL" if isinstance(acct, VirtualAccount) else "REAL"}

from account_manager import VirtualAccount

@app.get("/api/account/status")
def get_account_status():
    """Get balance and positions of current account."""
    acct = account_manager.get_account(CURRENT_ACCOUNT_ID)
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {
        "id": acct.account_id,
        "name": acct.name,
        "balance": acct.get_balance(),
        "positions": acct.get_positions(),
        "type": "VIRTUAL" if isinstance(acct, VirtualAccount) else "REAL"
    }

@app.get("/api/account/transactions")
def get_account_transactions():
    """Get transactions of current account."""
    # This method needs to be added to BaseAccount or directly use DBManager
    # Using DBManager directly for simplicity as BaseAccount might not cover history yet
    return db_manager.get_transactions(CURRENT_ACCOUNT_ID)

@app.post("/api/place_order")
def place_order(req: OrderRequest):
    print(f"🛒 Order Request: {req.action} {req.stock_code} at {req.price} x {req.quantity}")
    acct = account_manager.get_account(CURRENT_ACCOUNT_ID)
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")

    result = acct.place_order(
        req.stock_code,
        req.action,
        req.price,
        req.quantity,
        req.order_type,
        req.price_type
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
        
    return result

if __name__ == "__main__":
    print("🚀 Starting API Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
