from enum import Enum
import uuid
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Union


# Utility models
class UID(BaseModel):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)


class TStamp(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Exercises


class SetRepExercises(str, Enum):
    PUSH_UP = "pushup"
    PULL_OVER = "pullover"
    FRONT_RAISE = "frontraise"
    SHOULDER_TAPS = "shouldertaps"
    BATTLE_ROPES = "battleropes"
    BENCH_DIP = "benchdip"


class RunningExercises(str, Enum):
    OUTDOOR_RUNNING = "outdoor_running"
    TREADMILL = "treadmill"
    ELLIPTICAL = "elliptical"
    ELEVATED_TREADMILL = "elevated_treadmill"


class WeightExercises(str, Enum):
    DEADLIFT = "deadlift"
    BENCH_PRESS = "bench_press"


# Units
class DistanceUnit(str, Enum):
    KM = "km"
    MILES = "miles"


class WeightUnit(str, Enum):
    KG = "kg"
    LBS = "lbs"


# Log models
class SetRepLog(BaseModel):
    exercise: SetRepExercises
    sets: int = Field(1, gt=0)
    reps: int = Field(1, gt=0)
    duration_in_seconds: int = Field(600, gt=0)


class RunningLog(BaseModel):
    exercise: RunningExercises
    distance: int = Field(1, gt=0)
    unit: DistanceUnit = DistanceUnit.KM
    duration_in_seconds: int = Field(600, gt=0)


class WeightLog(SetRepLog):
    exercise: WeightExercises
    weight: int = Field(1, gt=0)
    unit: WeightUnit = WeightUnit.KG
    duration_in_seconds: int = Field(600, gt=0)


# Logs model
class ExerciseLogsRequest(BaseModel):
    exercises: list[SetRepLog | RunningLog | WeightLog]


class ExerciseLogs(ExerciseLogsRequest, UID, TStamp):
    user_email: EmailStr
