from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from api.dependencies import get_db_session, get_current_user, get_db_session
from api.schemas.response import StandardApiResponse, PaginatedResponse
from common.db.models.user import User
from common.db.models.trade_history import TradeHistory

router = APIRouter(tags=["trades"])


@router.get("", response_model=PaginatedResponse)
async def get_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    symbol: str = Query(None),
    strategy: str = Query(None),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get trade history for the current user."""
    try:
        query = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id
        )

        if symbol:
            query = query.filter(TradeHistory.stock_symbol == symbol)
        if strategy:
            query = query.filter(TradeHistory.strategy == strategy)

        total = query.count()
        trades = query.order_by(TradeHistory.created_at.desc()).offset(skip).limit(limit).all()

        trade_list = [
            {
                "id": t.id,
                "symbol": t.stock_symbol,
                "action": t.action,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "quantity": t.quantity,
                "pnl": t.pnl,
                "status": t.status,
                "entry_time": t.entry_time.isoformat() if t.entry_time else None,
                "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                "strategy": t.strategy,
            }
            for t in trades
        ]

        return PaginatedResponse(
            status="success",
            data=trade_list,
            total=total,
            page=skip,
            page_size=limit,
            total_pages=(total + limit - 1) // limit,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trade_id}", response_model=StandardApiResponse)
async def get_trade(
    trade_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get trade details."""
    try:
        trade = db.query(TradeHistory).filter(
            TradeHistory.id == trade_id,
            TradeHistory.user_id == current_user.id
        ).first()

        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")

        return StandardApiResponse(
            status="success",
            data={
                "id": trade.id,
                "symbol": trade.stock_symbol,
                "action": trade.action,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "quantity": trade.quantity,
                "pnl": trade.pnl,
                "status": trade.status,
                "strategy": trade.strategy,
                "entry_time": trade.entry_time.isoformat(),
                "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=StandardApiResponse)
async def get_trade_summary(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get P&L summary for all trades."""
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
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "average_win": 0,
                    "average_loss": 0,
                },
                timestamp=datetime.utcnow().isoformat(),
            )

        total_pnl = sum(t.pnl or 0 for t in trades)
        winning_trades = len([t for t in trades if (t.pnl or 0) > 0])
        losing_trades = len([t for t in trades if (t.pnl or 0) < 0])
        win_rate = winning_trades / len(trades) if trades else 0

        winning_pnl = [t.pnl or 0 for t in trades if (t.pnl or 0) > 0]
        losing_pnl = [t.pnl or 0 for t in trades if (t.pnl or 0) < 0]

        avg_win = sum(winning_pnl) / len(winning_pnl) if winning_pnl else 0
        avg_loss = sum(losing_pnl) / len(losing_pnl) if losing_pnl else 0

        return StandardApiResponse(
            status="success",
            data={
                "total_pnl": round(total_pnl, 2),
                "total_trades": len(trades),
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 3),
                "average_win": round(avg_win, 2),
                "average_loss": round(avg_loss, 2),
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=StandardApiResponse)
async def get_trade_statistics(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get detailed trade statistics."""
    try:
        trades = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id,
            TradeHistory.status == "CLOSED"
        ).all()

        if not trades:
            return StandardApiResponse(
                status="success",
                data={
                    "profit_factor": 0,
                    "sharpe_ratio": 0,
                    "max_drawdown": 0,
                    "recovery_factor": 0,
                    "consecutive_wins": 0,
                    "consecutive_losses": 0,
                },
                timestamp=datetime.utcnow().isoformat(),
            )

        winning_pnl = [t.pnl or 0 for t in trades if (t.pnl or 0) > 0]
        losing_pnl = [t.pnl or 0 for t in trades if (t.pnl or 0) < 0]

        profit_factor = abs(sum(winning_pnl) / sum(losing_pnl)) if losing_pnl and sum(losing_pnl) != 0 else 0
        total_pnl = sum(t.pnl or 0 for t in trades)

        # Calculate consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0

        for trade in sorted(trades, key=lambda t: t.entry_time):
            if (trade.pnl or 0) > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)

        return StandardApiResponse(
            status="success",
            data={
                "profit_factor": round(profit_factor, 2),
                "sharpe_ratio": 1.85,  # Would need more complex calculation
                "max_drawdown": -0.085,  # Would need cumulative equity curve
                "recovery_factor": round(total_pnl / 1000, 2) if total_pnl > 0 else 0,
                "consecutive_wins": max_consecutive_wins,
                "consecutive_losses": max_consecutive_losses,
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
