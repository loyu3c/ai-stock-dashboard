from abc import ABC, abstractmethod
from db_manager import DBManager
from shioaji_login import ShioajiLogin
import math

class BaseAccount(ABC):
    def __init__(self, account_id, name):
        self.account_id = account_id
        self.name = name
        self.db = DBManager()

    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def get_positions(self):
        pass

    @abstractmethod
    def place_order(self, stock_code, action, price, quantity, order_type="ROD", price_type="LMT"):
        pass

class VirtualAccount(BaseAccount):
    def __init__(self, account_id, name, fee_rate=0.001425, tax_rate=0.003):
        super().__init__(account_id, name)
        self.fee_rate = fee_rate
        self.tax_rate = tax_rate

    def get_balance(self):
        return self.db.get_account_balance(self.account_id)

    def get_positions(self):
        return self.db.get_all_positions(self.account_id)

    def place_order(self, stock_code, action, price, quantity, order_type="ROD", price_type="LMT"):
        """
        Simulate placing an order.
        For Virtual Account, we assume immediate fill at the given price for simplicity unless we want to simulate order matching.
        """
        if quantity <= 0:
            return {"status": "error", "message": "Quantity must be positive"}

        # Calculate Costs
        subtotal = price * quantity
        fee = math.floor(subtotal * self.fee_rate)
        # Min fee usually 20 TWD, but let's keep it simple or strictly follow rule
        if fee < 20: fee = 20 # Simple min fee rule
        
        tax = 0
        total_amount = 0

        current_balance = self.get_balance()

        if action == "BUY":
            total_amount = subtotal + fee
            if current_balance < total_amount:
                return {"status": "error", "message": f"Insufficient balance. Need {total_amount}, Have {current_balance}"}
            
            # Update Balance
            self.db.update_account_balance(self.account_id, -total_amount)
            # Update Position
            self.db.update_position(self.account_id, stock_code, quantity, price, "BUY")
            
        elif action == "SELL":
            tax = math.floor(subtotal * self.tax_rate)
            total_amount = subtotal - fee - tax
            
            # Check Position
            pos = self.db.get_position(self.account_id, stock_code)
            if not pos or pos['quantity'] < quantity:
                 return {"status": "error", "message": f"Insufficient position. Have {pos['quantity'] if pos else 0}"}

            # Update Balance
            self.db.update_account_balance(self.account_id, total_amount)
            # Update Position
            self.db.update_position(self.account_id, stock_code, -quantity, price, "SELL")
        
        else:
            return {"status": "error", "message": "Invalid action"}

        # Log Transaction
        # total_amount stored is positive for both buy (cost) and sell (proceeds) usually, 
        # or we can store net flow (negative for buy). 
        # The schema comment said: "Net amount (Cost for BUY, Proceeds for SELL)" -> Implies separate handling or absolute value?
        # Let's store the signed cash flow impact if we want, OR just the absolute magnitude as per schema comment description typically.
        # However, for 'transactions' table usually it's better to store the absolute money exchanged magnitude and let Action dictate direction.
        # I will store the ABSOLUTE amount that was deducted or added.
        
        self.db.log_transaction(
            self.account_id, 
            stock_code, 
            action, 
            price, 
            quantity, 
            fee, 
            tax, 
            total_amount, 
            f"Virtual Order: {action} {stock_code}"
        )

        return {
            "status": "success", 
            "message": f"Order Filled: {action} {stock_code}",
            "details": {
                "price": price,
                "quantity": quantity,
                "fee": fee,
                "tax": tax,
                "total": total_amount
            }
        }

import shioaji as sj

class RealAccount(BaseAccount):
    def __init__(self, account_id, name):
        super().__init__(account_id, name)
        # Shioaji login is singleton
        self.api = ShioajiLogin.get_api()

    def get_balance(self):
        try:
            # Shioaji account_balance returns a list of AccountBalance objects usually
            # But specific structure depends on version. Typically:
            # [{'acc_balance': 100000, 'date': '2024...', ...}]
            # In simulation mode, it might return mock data.
            bg = self.api.account_balance()
            if isinstance(bg, list) and len(bg) > 0:
                # Iterate to find the correct currency or sum up?
                # Usually we care about 'acc_balance' (Account Balance) or 'settle_net_amt' (Settlement Net Amount)
                # For simplicity, let's grab the first entry's acc_balance
                return float(bg[0].acc_balance)
            return 0.0
        except Exception as e:
            # In simulation, account_balance might not be supported or fail
            print(f"⚠️ [RealAccount] Balance fetch warning: {e}")
            return 0.0

    def get_positions(self):
        try:
            # unit=sj.constant.Unit.Share returns positions in shares
            positions = self.api.list_positions(unit=sj.constant.Unit.Share)
            result = []
            for pos in positions:
                result.append({
                    "stock_code": pos.code,
                    "quantity": int(pos.quantity),
                    "avg_cost": float(pos.price), # 'price' in position often refers to cost price
                    "market_value": float(pos.market_value) if hasattr(pos, 'market_value') else 0, # market_value might be calculated
                    "pnl": float(pos.pnl) if hasattr(pos, 'pnl') else 0
                })
            return result
        except Exception as e:
            print(f"❌ [RealAccount] Failed to fetch positions: {e}")
            return []

    def place_order(self, stock_code, action, price, quantity, order_type="ROD", price_type="LMT"):
        """
        Places a real order via Shioaji.
        """
        try:
            # 1. Construct Contract
            contract = self.api.Contracts.Stocks[stock_code]
            if not contract:
                return {"status": "error", "message": f"Contract not found for {stock_code}"}
            
            # 2. Construct Order
            action_enum = sj.constant.Action.Buy if action == "BUY" else sj.constant.Action.Sell
            price_type_enum = getattr(sj.constant.StockPriceType, price_type, sj.constant.StockPriceType.LMT)
            order_type_enum = getattr(sj.constant.OrderType, order_type, sj.constant.OrderType.ROD)
            
            order = self.api.Order(
                price=price,
                quantity=quantity,
                action=action_enum,
                price_type=price_type_enum,
                order_type=order_type_enum,
                account=self.api.stock_account
            )
            
            # 3. Place Order
            trade = self.api.place_order(contract, order)
            
            # 4. Return result
            # Trade object status needs to be checked
            return {
                "status": "success",
                "message": f"Real Order Placed: {trade.status.status}",
                "order_id": trade.order.seqno
            }
            
        except Exception as e:
            print(f"❌ [RealAccount] Failed to place order: {e}")
            return {"status": "error", "message": str(e)}

class AccountManager:
    def __init__(self):
        self.db = DBManager()

    def get_all_accounts(self):
        return self.db.get_accounts()

    def get_account(self, account_id):
        accounts = self.get_all_accounts()
        target = next((a for a in accounts if a['id'] == account_id), None)
        if not target:
            return None
        
        if target['type'] == 'VIRTUAL':
            return VirtualAccount(target['id'], target['name'])
        elif target['type'] == 'REAL':
            return RealAccount(target['id'], target['name'])
        
        return None
