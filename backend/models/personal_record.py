"""
PersonalRecord model for tracking personal bests.
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Numeric, Index, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.mixins import TimestampMixin
from backend.models.workout_session import WeightUnit
import enum


class RecordType(str, enum.Enum):
    """Personal record types."""
    ONE_RM = "1rm"
    MAX_WEIGHT = "max_weight"
    MAX_REPS = "max_reps"
    MAX_VOLUME = "max_volume"


class PersonalRecord(Base, TimestampMixin):
    """Personal record model for tracking PRs."""

    __tablename__ = "personal_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    set_id = Column(Integer, ForeignKey("sets.id"), nullable=False)  # Link to achieving set

    # PR type
    record_type = Column(SQLEnum(RecordType), nullable=False)

    # PR values
    weight = Column(Numeric(6, 2), nullable=False)
    reps = Column(Integer, nullable=False)
    calculated_1rm = Column(Numeric(6, 2), nullable=True)  # Epley/Brzycki formula
    volume = Column(Numeric(8, 2), nullable=True)  # weight * reps
    weight_unit = Column(SQLEnum(WeightUnit), nullable=False)

    # Metadata
    achieved_at = Column(DateTime, nullable=False, index=True)
    superseded_at = Column(DateTime, nullable=True)  # When new PR achieved
    is_current = Column(Boolean, default=True, index=True)

    # Relationships
    user = relationship("User", back_populates="personal_records")
    exercise = relationship("Exercise")
    set = relationship("Set")

    # Indexes
    __table_args__ = (
        Index("idx_user_exercise_current", "user_id", "exercise_id", "is_current", "record_type"),
    )

    def __repr__(self):
        return f"<PersonalRecord(id={self.id}, user_id={self.user_id}, exercise_id={self.exercise_id}, weight={self.weight}{self.weight_unit})>"
