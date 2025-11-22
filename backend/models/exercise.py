"""
Exercise model for the exercise library.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, CheckConstraint, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSON
from backend.database import Base
from backend.models.mixins import TimestampMixin, SoftDeleteMixin
import enum


class DifficultyLevel(str, enum.Enum):
    """Exercise difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class MuscleGroup(str, enum.Enum):
    """Primary muscle groups."""
    CHEST = "chest"
    BACK = "back"
    LEGS = "legs"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    CORE = "core"
    CARDIO = "cardio"


class Exercise(Base, TimestampMixin, SoftDeleteMixin):
    """Exercise model for the exercise library."""

    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Categorization
    primary_muscle_group = Column(SQLEnum(MuscleGroup), nullable=False, index=True)
    secondary_muscle_groups = Column(JSON, default=list)  # List of muscle group strings
    equipment_required = Column(String(50), nullable=True, index=True)
    difficulty_level = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)

    # Exercise type
    is_compound = Column(Boolean, default=True)
    is_bodyweight = Column(Boolean, default=False)

    # Media
    video_url = Column(String(255), nullable=True)
    thumbnail_url = Column(String(255), nullable=True)

    # Metadata
    is_custom = Column(Boolean, default=False)  # User-created vs default library
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_muscle_equipment", "primary_muscle_group", "equipment_required"),
        Index("idx_exercise_active", "is_deleted", "primary_muscle_group"),
    )

    def __repr__(self):
        return f"<Exercise(id={self.id}, name='{self.name}', muscle='{self.primary_muscle_group}')>"
