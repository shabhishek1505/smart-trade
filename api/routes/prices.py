from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api.dependencies import get_db_session, get_current_user, get_db_session
from api.schemas.response import StandardApiResponse
from common.db.models.user import User

router = APIRouter(tags=["prices"])


@router.get("/{symbol}", response_model=StandardApiResponse)
async def get_current_price(
    symbol: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get current price for a symbol."""
    try:
        # TODO: Fetch from PriceService cache or broker API
        # For now, return structured response
        return StandardApiResponse(
            status="success",
            data={
                "symbol": symbol,
                "price": 1885.50,
                "timestamp": datetime.utcnow().isoformat(),
                "bid": 1885.25,
                "ask": 1885.75,
                "day_high": 1895.00,
                "day_low": 1850.00,
                "previous_close": 1880.00,
                "change": 5.50,
                "change_percent": 0.29,
                "volume": 1500000,
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/chart", response_model=StandardApiResponse)
async def get_price_chart(
    symbol: str,
    period: str = Query("1D", regex="^(1D|5D|1M|3M|6M|1Y)$"),
    interval: str = Query("1H", regex="^(1M|5M|15M|1H|1D)$"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get historical OHLC data for charting."""
    try:
        # TODO: Fetch historical data from broker or database
        mock_data = []
        current_time = datetime.utcnow()
        base_price = 1850.0

        for i in range(30):
            time = current_time - timedelta(hours=i)
            mock_data.insert(
                0,
                {
                    "time": time.isoformat(),
                    "open": base_price + (i * 0.5),
                    "high": base_price + (i * 0.5) + 5,
                    "low": base_price + (i * 0.5) - 3,
                    "close": base_price + (i * 0.5) + 2.5,
                    "volume": 1000000 + (i * 10000),
                },
            )

        return StandardApiResponse(
            status="success",
            data={
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data": mock_data,
            },
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
