"""
Reusable model mixins for timestamps and soft deletes.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Boolean


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps to models."""

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at = Column(DateTime, nullable=True, index=True)
    is_deleted = Column(Boolean, default=False, server_default='0', index=True)

    def soft_delete(self):
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
