from pydantic import BaseModel
from typing import Optional, Dict, Any

class StrategyTriggerData(BaseModel):
    plan_id: int
    strategy_id: int
    strategy_name: str
    stock_symbol: str
    override_params: Optional[Dict[str, Any]] = None
