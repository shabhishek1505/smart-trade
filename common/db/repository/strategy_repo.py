from sqlalchemy.orm import Session
from common.db.models.strategy import StrategyMaster, StrategyPlan

from sqlalchemy.orm import Session, joinedload
from common.db.models import StrategyPlan, StrategyMaster

def get_enabled_strategy_plans(db: Session):
    # Option 1: Use joinedload to eager load the related strategy_master
    plans = db.query(StrategyPlan)\
          .options(joinedload(StrategyPlan.strategy_master))\
          .filter(StrategyPlan.enabled == True).all()
    
    return plans

