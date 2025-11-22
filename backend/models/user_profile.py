"""
UserProfile model for extended user information.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.mixins import TimestampMixin
from backend.models.exercise import DifficultyLevel
import enum


class Gender(str, enum.Enum):
    """Gender options."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class UnitSystem(str, enum.Enum):
    """Unit system preferences."""
    METRIC = "metric"
    IMPERIAL = "imperial"


class WeightUnit(str, enum.Enum):
    """Weight unit preferences."""
    KG = "kg"
    LBS = "lbs"


class UserProfile(Base, TimestampMixin):
    """Extended user profile information."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Personal info
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)

    # Body measurements
    height_cm = Column(Integer, nullable=True)
    current_weight_kg = Column(Numeric(5, 2), nullable=True)
    goal_weight_kg = Column(Numeric(5, 2), nullable=True)

    # Preferences
    preferred_unit_system = Column(SQLEnum(UnitSystem), default=UnitSystem.METRIC)
    preferred_weight_unit = Column(SQLEnum(WeightUnit), default=WeightUnit.KG)

    # Training preferences
    experience_level = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    training_goals = Column(JSON, default=list)  # ['strength', 'hypertrophy', 'endurance']

    # Media
    profile_photo_url = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"
