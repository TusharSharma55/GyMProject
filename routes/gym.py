from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from db import DB
from models.auth import User
from config import GYM_COLLECTION
from schemas.schema import FastAPIAuth as mg
from models.gym import ExerciseLogsRequest, ExerciseLogs


gym_router = APIRouter(tags=['gym'], prefix="/gym")


def validate_existing_log(existing_log, current_user):
    if not existing_log:
        raise HTTPException(
            status_code=404, detail=f"Log not found")
    if ExerciseLogs(**existing_log).user_email != current_user.email:
        raise HTTPException(status_code=403, detail="Forbidden")


@gym_router.get("/logs", response_model=list[ExerciseLogs])
async def get_all_logs(
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    records = DB.get_records(GYM_COLLECTION, "user_email", current_user.email)
    new_records = []
    for l in records:
        try:
            new_records.append(ExerciseLogs(**l))
        except:
            pass
    return new_records


@gym_router.get("/logs/{uid}", response_model=ExerciseLogs)
async def get_logs(
    uid: str,
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    existing_log = DB.get_record(GYM_COLLECTION, "uid", uid)
    validate_existing_log(existing_log=existing_log, current_user=current_user)
    return ExerciseLogs(**existing_log)


@gym_router.post("/logs", response_model=ExerciseLogs)
async def create_logs(
    logs: ExerciseLogsRequest,
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    logs = ExerciseLogs(
        exercises=logs.exercises,
        user_email=current_user.email
    )
    print("Checking:- ", type(logs))
    DB.insert_record(GYM_COLLECTION, logs)
    return logs


@gym_router.patch("/logs", response_model=ExerciseLogs)
async def update_logs(
    uid: str,
    logs: ExerciseLogsRequest,
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    existing_log = DB.get_record(GYM_COLLECTION, "uid", str(uid))
    validate_existing_log(existing_log=existing_log, current_user=current_user)
    logs = ExerciseLogs(
        uid=uid,
        exercises=logs.exercises,
        user_email=current_user.email,
    )
    DB.update_record(GYM_COLLECTION, logs, "uid")
    return logs


@gym_router.delete("/logs", status_code=204)
async def delete_logs(
    uid: str,
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    existing_log = DB.get_record(GYM_COLLECTION, "uid", uid)
    validate_existing_log(existing_log=existing_log, current_user=current_user)
    DB.delete_record(GYM_COLLECTION, "uid", uid)
    return {"message": f" Current - {uid} log get Delected."}
