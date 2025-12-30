from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sheet_manager import SheetManager
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

sheet_manager = SheetManager()

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
        ws = sheet_manager.sh.worksheet("Stock List")
        raw_stocks = ws.get_all_records()
        
        # Strategy
        strategy = sheet_manager.fetch_strategy_config()
        
        return {
            "stock_list": raw_stocks,
            "strategy": strategy
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save_stock_list")
def save_stock_list(items: list[StockItem]):
    """Saves the full stock list."""
    # Convert Pydantic models to clean dicts for sheet format
    data = []
    for item in items:
        row = item.dict()
        # Normalize to Strings for Sheet
        row['Stock'] = str(row['Stock'])
        # Normalize Enabled to "TRUE" / "FALSE"
        is_enabled = str(row['Enabled']).upper() == 'TRUE' or row['Enabled'] is True
        row['Enabled'] = "TRUE" if is_enabled else "FALSE"
        # Handle potential None
        row['Name'] = str(row['Name']) if row['Name'] is not None else ""
        row['Memo'] = str(row['Memo']) if row['Memo'] is not None else ""
        data.append(row)

    success = sheet_manager.save_stock_list(data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save stock list")
    return {"status": "success"}

@app.post("/api/save_strategy")
def save_strategy(data: StrategyConfig):
    """Saves strategy configuration."""
    success = sheet_manager.save_strategy_config(data.config)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save strategy")
    return {"status": "success"}

if __name__ == "__main__":
    print("🚀 Starting API Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
