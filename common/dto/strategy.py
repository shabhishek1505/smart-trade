from pydantic import BaseModel
from typing import Optional, Dict, Any

class StrategyTriggerData(BaseModel):
    strategy_id: int
    stock_symbol: str
    override_params: Optional[Dict[str, Any]] = None
