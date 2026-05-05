from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from api.dependencies import get_db_session, get_current_user, get_db_session
from api.schemas.response import StandardApiResponse, PaginatedResponse
from common.db.models.user import User
from common.db.models.strategy_signal import StrategySignal

router = APIRouter(tags=["signals"])


@router.get("", response_model=PaginatedResponse)
async def get_signals(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get paginated list of signals for the current user."""
    try:
        query = db.query(StrategySignal).filter(
            StrategySignal.user_id == current_user.id
        )

        if status:
            query = query.filter(StrategySignal.status == status)

        total = query.count()
        signals = query.order_by(StrategySignal.timestamp.desc()).offset(skip).limit(limit).all()

        signal_list = [
            {
                "id": s.id,
                "symbol": s.stock_symbol,
                "signal_type": s.signal_type,
                "confidence": s.confidence,
                "price": s.price,
                "status": s.status,
                "timestamp": s.timestamp.isoformat() if s.timestamp else None,
                "strategy": f"strategy_{s.strategy_id}",
                "reason": s.reason,
            }
            for s in signals
        ]

        return PaginatedResponse(
            status="success",
            data=signal_list,
            total=total,
            page=skip,
            page_size=limit,
            total_pages=(total + limit - 1) // limit,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{signal_id}/execute", response_model=StandardApiResponse)
async def execute_signal(
    signal_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Execute a pending signal."""
    try:
        signal = db.query(StrategySignal).filter(
            StrategySignal.id == signal_id,
            StrategySignal.user_id == current_user.id
        ).first()

        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")

        if signal.status != "PENDING":
            raise HTTPException(status_code=400, detail="Signal is not pending")

        # Update signal status
        signal.status = "EXECUTED"
        signal.executed = True
        signal.executed_at = datetime.utcnow()
        db.commit()

        return StandardApiResponse(
            status="success",
            data={"signal_id": signal_id, "status": "EXECUTED"},
            message="Signal executed successfully",
            timestamp=datetime.utcnow().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{signal_id}/cancel", response_model=StandardApiResponse)
async def cancel_signal(
    signal_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Cancel a pending signal."""
    try:
        signal = db.query(StrategySignal).filter(
            StrategySignal.id == signal_id,
            StrategySignal.user_id == current_user.id
        ).first()

        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")

        if signal.status != "PENDING":
            raise HTTPException(status_code=400, detail="Signal is not pending")

        # Update signal status
        signal.status = "CANCELLED"
        db.commit()

        return StandardApiResponse(
            status="success",
            data={"signal_id": signal_id, "status": "CANCELLED"},
            message="Signal cancelled successfully",
            timestamp=datetime.utcnow().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
