"""
WorkoutProgram and ProgramExercise models.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.mixins import TimestampMixin, SoftDeleteMixin
from backend.models.exercise import DifficultyLevel


class WorkoutProgram(Base, TimestampMixin, SoftDeleteMixin):
    """Workout program model."""

    __tablename__ = "workout_programs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Program metadata
    duration_weeks = Column(Integer, nullable=True)
    sessions_per_week = Column(Integer, nullable=True)
    difficulty_level = Column(SQLEnum(DifficultyLevel), nullable=True)

    # Sharing and templates
    is_template = Column(Boolean, default=False)  # Template vs active program
    is_public = Column(Boolean, default=False)  # Shareable
    cloned_from_id = Column(Integer, ForeignKey("workout_programs.id"), nullable=True)

    # Status tracking
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    user = relationship("User", back_populates="programs")
    sessions = relationship("WorkoutSession", back_populates="program")
    exercises = relationship("ProgramExercise", back_populates="program", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkoutProgram(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class ProgramExercise(Base, TimestampMixin):
    """Join table for program exercises with prescription details."""

    __tablename__ = "program_exercises"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("workout_programs.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)

    # Exercise prescription
    order_index = Column(Integer, nullable=False)  # Order within program
    target_sets = Column(Integer, nullable=True)
    target_reps = Column(String(20), nullable=True)  # "8-12" or "10"
    target_rpe = Column(Integer, nullable=True)
    rest_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    program = relationship("WorkoutProgram", back_populates="exercises")
    exercise = relationship("Exercise")

    # Constraints
    __table_args__ = (
        UniqueConstraint("program_id", "exercise_id", "order_index", name="unique_program_exercise_order"),
        Index("idx_program_order", "program_id", "order_index"),
    )

    def __repr__(self):
        return f"<ProgramExercise(program_id={self.program_id}, exercise_id={self.exercise_id}, order={self.order_index})>"
