"""Common API response schemas"""

from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime


class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    status: str  # "success" or "error"
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {"id": 1, "name": "example"},
                "message": "Operation successful",
                "timestamp": "2026-04-10T12:00:00Z"
            }
        }


class PaginatedResponse(BaseModel):
    """Paginated response"""
    status: str
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "timestamp": "2026-04-10T12:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    status: str = "error"
    code: str
    message: str
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": "INVALID_REQUEST",
                "message": "Invalid request parameters",
                "timestamp": "2026-04-10T12:00:00Z"
            }
        }


# Alias for backward compatibility
StandardApiResponse = ApiResponse
