"""
WorkoutSession and Set models for logging workouts.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, Date, DateTime,
    Numeric, CheckConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.mixins import TimestampMixin, SoftDeleteMixin
import enum


class SessionMood(str, enum.Enum):
    """Session mood ratings."""
    GREAT = "great"
    GOOD = "good"
    OKAY = "okay"
    POOR = "poor"


class WeightUnit(str, enum.Enum):
    """Weight units."""
    KG = "kg"
    LBS = "lbs"


class WorkoutSession(Base, TimestampMixin, SoftDeleteMixin):
    """Workout session model."""

    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("workout_programs.id"), nullable=True, index=True)

    # Session metadata
    name = Column(String(100), nullable=False)
    session_date = Column(Date, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Session quality metrics
    overall_rpe = Column(Integer, nullable=True)  # Session RPE (1-10)
    notes = Column(Text, nullable=True)
    mood = Column(SQLEnum(SessionMood), nullable=True)

    # Status
    is_completed = Column(Boolean, default=False, index=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    program = relationship("WorkoutProgram", back_populates="sessions")
    sets = relationship("Set", back_populates="session", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_user_date", "user_id", "session_date"),
        Index("idx_user_completed", "user_id", "is_completed", "session_date"),
    )

    def __repr__(self):
        return f"<WorkoutSession(id={self.id}, name='{self.name}', date={self.session_date})>"


class Set(Base, TimestampMixin):
    """Individual set model."""

    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)

    # Set data
    set_number = Column(Integer, nullable=False)  # 1st, 2nd, 3rd set
    weight = Column(Numeric(6, 2), nullable=False)  # Up to 9999.99 kg/lbs
    reps = Column(Integer, nullable=False)
    rpe = Column(Integer, nullable=True)  # Rate of Perceived Exertion (1-10)

    # Additional metrics
    rest_seconds = Column(Integer, nullable=True)
    distance_meters = Column(Integer, nullable=True)  # For cardio
    duration_seconds = Column(Integer, nullable=True)  # For timed exercises
    tempo = Column(String(10), nullable=True)  # "3-0-1-0" (eccentric-pause-concentric-pause)

    # Metadata
    is_warmup = Column(Boolean, default=False)
    is_dropset = Column(Boolean, default=False)
    is_failure = Column(Boolean, default=False)
    notes = Column(String(255), nullable=True)

    # Weight unit tracking (CRITICAL!)
    weight_unit = Column(SQLEnum(WeightUnit), nullable=False, default=WeightUnit.KG)

    # Relationships
    session = relationship("WorkoutSession", back_populates="sets")
    exercise = relationship("Exercise")

    # Constraints
    __table_args__ = (
        CheckConstraint("weight >= 0", name="weight_positive"),
        CheckConstraint("reps >= 0 AND reps <= 1000", name="reps_range"),
        CheckConstraint("rpe IS NULL OR (rpe >= 1 AND rpe <= 10)", name="rpe_range"),
        Index("idx_session_exercise_set", "session_id", "exercise_id", "set_number"),
        Index("idx_exercise_weight", "exercise_id", "weight"),  # For PR queries
    )

    def __repr__(self):
        return f"<Set(id={self.id}, exercise_id={self.exercise_id}, weight={self.weight}{self.weight_unit}, reps={self.reps})>"
