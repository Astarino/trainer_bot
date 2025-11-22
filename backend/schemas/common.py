"""
Common response schemas following CLAUDE.md standards.
"""
from typing import TypeVar, Generic, Optional, List, Any
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response format."""
    success: bool = True
    data: T
    meta: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "Example"},
                "meta": {"timestamp": "2025-01-22T10:30:00Z"}
            }
        }


class ErrorDetail(BaseModel):
    """Error detail for field-level errors."""
    field: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = False
    error: dict

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid data",
                    "details": [
                        {"field": "email", "message": "Invalid email format"}
                    ]
                }
            }
        }


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    per_page: int
    total_pages: int
    total_items: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response format."""
    success: bool = True
    data: List[T]
    pagination: PaginationMeta
