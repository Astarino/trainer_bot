"""
Database models for the Fitness Trainer application.
"""
from backend.models.mixins import TimestampMixin, SoftDeleteMixin
from backend.models.user import User
from backend.models.exercise import Exercise
from backend.models.workout_program import WorkoutProgram, ProgramExercise
from backend.models.workout_session import WorkoutSession, Set
from backend.models.personal_record import PersonalRecord
from backend.models.user_profile import UserProfile

__all__ = [
    "TimestampMixin",
    "SoftDeleteMixin",
    "User",
    "Exercise",
    "WorkoutProgram",
    "ProgramExercise",
    "WorkoutSession",
    "Set",
    "PersonalRecord",
    "UserProfile",
]
