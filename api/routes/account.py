from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from api.dependencies import get_db_session, get_current_user, get_db_session
from api.schemas.response import StandardApiResponse
from common.db.models.user import User
from common.db.models.position import Position
from common.db.models.trade_history import TradeHistory

router = APIRouter(tags=["account"])


@router.get("/balance", response_model=StandardApiResponse)
async def get_balance(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get account balance and capital information."""
    try:
        # Get all trades for P&L calculation
        closed_trades = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id,
            TradeHistory.status == "CLOSED"
        ).all()

        # Get open positions
        positions = db.query(Position).filter(
            Position.user_id == current_user.id
        ).all()

        # Calculate realized P&L from closed trades
        realized_pnl = sum(t.pnl or 0 for t in closed_trades)

        # Calculate unrealized P&L from open positions
        unrealized_pnl = sum(
            (p.current_value or 0) - (p.invested_value or 0)
            for p in positions
        )

        # Calculate total P&L
        total_pnl = realized_pnl + unrealized_pnl

        # Calculate used capital (from open positions) and available capital
        used_capital = sum(p.invested_value or 0 for p in positions)
        total_balance = 500000  # Starting balance - in real app would be from settings
        available_capital = total_balance - used_capital

        return StandardApiResponse(
            status="success",
            data={
                "total_balance": round(total_balance + total_pnl, 2),
                "available_capital": round(available_capital, 2),
                "used_capital": round(used_capital, 2),
                "margin_available": round(available_capital * 2, 2),  # 2x margin
                "unrealized_pnl": round(unrealized_pnl, 2),
                "realized_pnl": round(realized_pnl, 2),
                "currency": "INR",
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info", response_model=StandardApiResponse)
async def get_account_info(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get account information."""
    try:
        # Get trade count
        total_trades = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id
        ).count()

        # Count trades today for day trades check
        from datetime import date
        today = date.today()
        day_trades = db.query(TradeHistory).filter(
            TradeHistory.user_id == current_user.id,
            TradeHistory.entry_time >= datetime.combine(today, datetime.min.time())
        ).count()

        return StandardApiResponse(
            status="success",
            data={
                "username": current_user.username,
                "email": current_user.email,
                "account_type": "Regular",
                "status": "Active" if current_user.is_active else "Inactive",
                "created_at": current_user.created_at.isoformat(),
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
                "total_trades": total_trades,
                "day_trades_count": day_trades,
                "max_day_trades": 5,
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
