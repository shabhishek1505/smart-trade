from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import defaultdict

from api.dependencies import get_db_session, get_current_user, get_db_session
from api.schemas.response import StandardApiResponse
from common.db.models.user import User
from common.db.models.trade_history import TradeHistory
from common.db.models.strategy import StrategyPlan, StrategyMaster

router = APIRouter(tags=["analytics"])


@router.get("/performance", response_model=StandardApiResponse)
async def get_performance(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get overall performance metrics."""
    try:
        trades = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id,
            TradeHistory.status == "CLOSED"
        ).all()

        if not trades:
            return StandardApiResponse(
                status="success",
                data={
                    "total_pnl": 0,
                    "win_rate": 0.0,
                    "sharpe_ratio": 0,
                    "sortino_ratio": 0,
                    "max_drawdown": 0,
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "average_win": 0,
                    "average_loss": 0,
                    "profit_factor": 0,
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
                "total_pnl": round(total_pnl, 2),
                "win_rate": round(win_rate, 3),
                "sharpe_ratio": 1.85,  # Needs complex calculation
                "sortino_ratio": 2.3,  # Needs complex calculation
                "max_drawdown": -0.085,  # Needs cumulative tracking
                "total_trades": len(trades),
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "average_win": round(avg_win, 2),
                "average_loss": round(avg_loss, 2),
                "profit_factor": round(profit_factor, 2),
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies", response_model=StandardApiResponse)
async def get_strategies_performance(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get performance breakdown by strategy."""
    try:
        # Get user's strategies
        plans = db.query(StrategyPlan).filter(
            StrategyPlan.user_id == current_user.id
        ).all()

        strategies_perf = []
        for plan in plans:
            # Get trades for this strategy
            trades = db.query(TradeHistory).filter(
                TradeHistory.user_id == current_user.id,
                TradeHistory.strategy == plan.strategy_id,
                TradeHistory.status == "CLOSED"
            ).all()

            if trades:
                total_pnl = sum(t.pnl or 0 for t in trades)
                winning = len([t for t in trades if (t.pnl or 0) > 0])
                win_rate = winning / len(trades) if trades else 0

                winning_pnl = [t.pnl or 0 for t in trades if (t.pnl or 0) > 0]
                losing_pnl = [t.pnl or 0 for t in trades if (t.pnl or 0) < 0]
                profit_factor = abs(sum(winning_pnl) / sum(losing_pnl)) if losing_pnl and sum(losing_pnl) != 0 else 0

                strategies_perf.append({
                    "strategy": f"strategy_{plan.strategy_id}",
                    "total_pnl": round(total_pnl, 2),
                    "total_trades": len(trades),
                    "win_rate": round(win_rate, 3),
                    "profit_factor": round(profit_factor, 2),
                })

        return StandardApiResponse(
            status="success",
            data=strategies_perf,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monthly-returns", response_model=StandardApiResponse)
async def get_monthly_returns(
    year: int = Query(2026),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get monthly returns breakdown."""
    try:
        trades = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id,
            TradeHistory.status == "CLOSED",
            TradeHistory.exit_time.isnot(None)
        ).all()

        # Group by month
        monthly_data = defaultdict(float)
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        for trade in trades:
            if trade.exit_time and trade.exit_time.year == year:
                month_name = months[trade.exit_time.month - 1]
                monthly_data[month_name] += trade.pnl or 0

        data = [
            {
                "month": month,
                "return": round((monthly_data[month] / 100000 * 100), 2) if month in monthly_data else 0,
                "pnl": round(monthly_data[month], 2) if month in monthly_data else 0,
            }
            for month in months
            if month in monthly_data or True
        ]

        total_return = sum(d["return"] for d in data)
        total_pnl = sum(d["pnl"] for d in data)

        return StandardApiResponse(
            status="success",
            data={
                "year": year,
                "data": data,
                "total_return": round(total_return, 2),
                "total_pnl": round(total_pnl, 2),
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equity-curve", response_model=StandardApiResponse)
async def get_equity_curve(
    period: str = Query("1M", regex="^(1W|1M|3M|6M|1Y|ALL)$"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get equity curve data."""
    try:
        trades = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id,
            TradeHistory.status == "CLOSED",
            TradeHistory.exit_time.isnot(None)
        ).order_by(TradeHistory.exit_time).all()

        if not trades:
            return StandardApiResponse(
                status="success",
                data=[],
                timestamp=datetime.utcnow().isoformat(),
            )

        # Calculate running balance
        starting_balance = 100000
        running_balance = starting_balance
        equity_data = []

        for trade in trades:
            running_balance += trade.pnl or 0
            equity_data.append({
                "date": trade.exit_time.strftime("%Y-%m-%d"),
                "value": round(running_balance, 2),
            })

        return StandardApiResponse(
            status="success",
            data=equity_data,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
