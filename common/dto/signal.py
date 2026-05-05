from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class StrategySignalData(BaseModel):
    plan_id: int
    strategy_id: int
    strategy_name: str
    stock_symbol: str
    signal: str  # "BUY", "SELL", "HOLD"
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    price: float  # LTP at time of evaluation
    upper_bound_price: Optional[float] = None
    lower_bound_price: Optional[float] = None
    reason: Optional[str] = None
    evaluated_at: datetime
    additional_data: Optional[Any] = None

    # Multi-user broker integration
    user_id: Optional[int] = None  # User placing the trade
    broker_type: str = "angel_one"  # Broker to use
    order_type: str = "MARKET"  # MARKET, LIMIT, STOPLOSS
