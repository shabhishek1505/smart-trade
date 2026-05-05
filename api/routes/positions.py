from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from api.dependencies import get_db_session, get_current_user, get_db_session
from api.schemas.response import StandardApiResponse, PaginatedResponse
from common.db.models.user import User
from common.db.models.position import Position

router = APIRouter(tags=["positions"])


@router.get("", response_model=PaginatedResponse)
async def get_positions(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get current open positions for the user."""
    try:
        positions = db.query(Position).filter(
            Position.user_id == current_user.id
        ).order_by(Position.created_at.desc()).all()

        position_list = [
            {
                "id": p.id,
                "symbol": p.symbol,
                "quantity": p.quantity,
                "average_price": p.average_price,
                "current_price": p.current_price,
                "invested_value": p.invested_value,
                "current_value": p.current_value,
                "entry_time": p.entry_time.isoformat() if p.entry_time else None,
                "strategy": p.strategy,
            }
            for p in positions
        ]

        return PaginatedResponse(
            status="success",
            data=position_list,
            total=len(positions),
            page=0,
            page_size=100,
            total_pages=1,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=StandardApiResponse)
async def get_positions_summary(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get portfolio summary for all positions."""
    try:
        positions = db.query(Position).filter(
            Position.user_id == current_user.id
        ).all()

        if not positions:
            return StandardApiResponse(
                status="success",
                data={
                    "total_positions": 0,
                    "total_invested": 0,
                    "total_current_value": 0,
                    "total_unrealized_pnl": 0,
                    "total_unrealized_pnl_percent": 0.0,
                },
                timestamp=datetime.utcnow().isoformat(),
            )

        total_invested = sum(p.invested_value or 0 for p in positions)
        total_current_value = sum(p.current_value or 0 for p in positions)
        total_unrealized_pnl = total_current_value - total_invested
        pnl_percent = (total_unrealized_pnl / total_invested * 100) if total_invested > 0 else 0

        return StandardApiResponse(
            status="success",
            data={
                "total_positions": len(positions),
                "total_invested": round(total_invested, 2),
                "total_current_value": round(total_current_value, 2),
                "total_unrealized_pnl": round(total_unrealized_pnl, 2),
                "total_unrealized_pnl_percent": round(pnl_percent, 2),
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{position_id}/close", response_model=StandardApiResponse)
async def close_position(
    position_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Close an open position."""
    try:
        position = db.query(Position).filter(
            Position.id == position_id,
            Position.user_id == current_user.id
        ).first()

        if not position:
            raise HTTPException(status_code=404, detail="Position not found")

        # Delete the position
        db.delete(position)
        db.commit()

        return StandardApiResponse(
            status="success",
            data={"position_id": position_id, "status": "CLOSED"},
            message="Position closed successfully",
            timestamp=datetime.utcnow().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
