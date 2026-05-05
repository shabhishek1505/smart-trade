from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from api.dependencies import get_db_session, get_current_user, get_db_session
from api.schemas.response import StandardApiResponse, PaginatedResponse
from common.db.models.user import User
from common.db.models.strategy import StrategyMaster, StrategyPlan
from common.db.models.trade_history import TradeHistory

router = APIRouter(tags=["strategies"])


@router.get("", response_model=PaginatedResponse)
async def get_strategies(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get list of user's enabled strategies."""
    try:
        # Query user's strategy plans with strategy details
        plans = db.query(
            StrategyPlan,
            StrategyMaster.strategy_name,
            StrategyMaster.description
        ).join(
            StrategyMaster,
            StrategyPlan.strategy_id == StrategyMaster.strategy_id
        ).filter(
            StrategyPlan.user_id == current_user.id
        ).all()

        strategies = []
        for plan, strategy_name, description in plans:
            strategies.append({
                "name": strategy_name,
                "enabled": plan.enabled,
                "signals": plan.total_signals,
                "win_rate": plan.win_rate,
                "description": description,
                "total_trades": plan.total_trades,
                "pnl": plan.total_pnl,
            })

        return PaginatedResponse(
            status="success",
            data=strategies,
            total=len(strategies),
            page=0,
            page_size=100,
            total_pages=1,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_name}", response_model=StandardApiResponse)
async def get_strategy(
    strategy_name: str = Path(...),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get strategy details."""
    try:
        # Query strategy master details
        strategy = db.query(StrategyMaster).filter(
            StrategyMaster.strategy_name == strategy_name
        ).first()

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return StandardApiResponse(
            status="success",
            data={
                "name": strategy.strategy_name,
                "description": strategy.description,
                "default_cron": strategy.default_cron,
                "parameters": strategy.default_params or {},
                "created_at": strategy.created_at.isoformat(),
                "updated_at": strategy.updated_at.isoformat(),
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{strategy_name}/start", response_model=StandardApiResponse)
async def start_strategy(
    strategy_name: str = Path(...),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Enable and start a strategy."""
    try:
        # Get strategy master
        strategy = db.query(StrategyMaster).filter(
            StrategyMaster.strategy_name == strategy_name
        ).first()

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # Update user's strategy plans
        db.query(StrategyPlan).filter(
            StrategyPlan.user_id == current_user.id,
            StrategyPlan.strategy_id == strategy.strategy_id
        ).update({"enabled": True})

        db.commit()

        return StandardApiResponse(
            status="success",
            data={"strategy": strategy_name, "status": "STARTED"},
            message=f"Strategy {strategy_name} started successfully",
            timestamp=datetime.utcnow().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{strategy_name}/stop", response_model=StandardApiResponse)
async def stop_strategy(
    strategy_name: str = Path(...),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Disable and stop a strategy."""
    try:
        # Get strategy master
        strategy = db.query(StrategyMaster).filter(
            StrategyMaster.strategy_name == strategy_name
        ).first()

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # Update user's strategy plans
        db.query(StrategyPlan).filter(
            StrategyPlan.user_id == current_user.id,
            StrategyPlan.strategy_id == strategy.strategy_id
        ).update({"enabled": False})

        db.commit()

        return StandardApiResponse(
            status="success",
            data={"strategy": strategy_name, "status": "STOPPED"},
            message=f"Strategy {strategy_name} stopped successfully",
            timestamp=datetime.utcnow().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_name}/performance", response_model=StandardApiResponse)
async def get_strategy_performance(
    strategy_name: str = Path(...),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get performance metrics for a strategy."""
    try:
        # Get strategy master
        strategy = db.query(StrategyMaster).filter(
            StrategyMaster.strategy_name == strategy_name
        ).first()

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # Query trades for this user and strategy
        trades = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id,
            TradeHistory.strategy == strategy_name,
            TradeHistory.status == "CLOSED"
        ).all()

        if not trades:
            return StandardApiResponse(
                status="success",
                data={
                    "strategy": strategy_name,
                    "total_pnl": 0,
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "average_win": 0,
                    "average_loss": 0,
                    "profit_factor": 0,
                    "sharpe_ratio": 0,
                    "max_drawdown": 0,
                },
                timestamp=datetime.utcnow().isoformat(),
            )

        # Calculate metrics
        total_pnl = sum(t.pnl or 0 for t in trades)
        winning_trades = len([t for t in trades if (t.pnl or 0) > 0])
        losing_trades = len([t for t in trades if (t.pnl or 0) < 0])
        win_rate = winning_trades / len(trades) if trades else 0

        winning_pnl = [t.pnl or 0 for t in trades if (t.pnl or 0) > 0]
        losing_pnl = [t.pnl or 0 for t in trades if (t.pnl or 0) < 0]

        avg_win = sum(winning_pnl) / len(winning_pnl) if winning_pnl else 0
        avg_loss = sum(losing_pnl) / len(losing_pnl) if losing_pnl else 0

        profit_factor = abs(sum(winning_pnl) / sum(losing_pnl)) if losing_pnl and sum(losing_pnl) != 0 else 0

        return StandardApiResponse(
            status="success",
            data={
                "strategy": strategy_name,
                "total_pnl": total_pnl,
                "total_trades": len(trades),
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 3),
                "average_win": round(avg_win, 2),
                "average_loss": round(avg_loss, 2),
                "profit_factor": round(profit_factor, 2),
                "sharpe_ratio": 0,  # Would require more data
                "max_drawdown": 0,  # Would require cumulative calculations
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
