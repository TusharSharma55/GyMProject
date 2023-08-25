from typing import Annotated
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from db import DB
from models.auth import User
from config import GYM_COLLECTION
from schemas.schema import FastAPIAuth as mg
from models.gym import ExerciseLogsRequest, ExerciseLogs
from logging_config import formater, file_handler

logger = logging.getLogger(__name__)
file_handler.setFormatter(formater)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


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
        except Exception as e:
            logger.error(f"Error parsing record: {e}")

    logger.info(
        f"Retrieved {len(new_records)} records for user: {current_user.email}")
    return new_records


@gym_router.get("/logs/{uid}", response_model=ExerciseLogs)
async def get_logs(
    uid: str,
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    logger.info(
        f"User {current_user.email} is attempting to retrieve log with UID {uid}")
    existing_log = DB.get_record(GYM_COLLECTION, "uid", uid)
    if existing_log is None:
        logger.warning(
            f"User {current_user.email} requested non-existent log with UID {uid}")
        raise HTTPException(status_code=404, detail="Log not found")

    validate_existing_log(existing_log=existing_log, current_user=current_user)
    logger.info(
        f"User {current_user.email} successfully retrieved log with UID {uid}")
    return ExerciseLogs(**existing_log)


@gym_router.post("/logs", response_model=ExerciseLogs)
async def create_logs(
    logs: ExerciseLogsRequest,
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    logger.info(f"Creating exercise logs for user {current_user.email}")
    logs = ExerciseLogs(
        exercises=logs.exercises,
        user_email=current_user.email
    )
    DB.insert_record(GYM_COLLECTION, logs)
    logger.info(f"Exercise logs created for user {current_user.email}")
    return logs


@gym_router.patch("/logs", response_model=ExerciseLogs)
async def update_logs(
    uid: str,
    logs_: ExerciseLogsRequest,
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    existing_log = DB.get_record(GYM_COLLECTION, "uid", str(uid))
    validate_existing_log(existing_log=existing_log, current_user=current_user)
    logs = ExerciseLogs(
        uid=uid,
        exercises=logs_.exercises,
        user_email=current_user.email,
    )
    logger.info(f"Updating log with UID: {uid} for user: {current_user.email}")

    DB.update_record(GYM_COLLECTION, logs, "uid")
    logger.info(
        f"Log with UID: {uid} updated successfully for user: {current_user.email}")
    return logs


@gym_router.delete("/logs", status_code=204)
async def delete_logs(
    uid: str,
    current_user: Annotated[User, Depends(mg.get_current_active_user)]
):
    try:
        existing_log = DB.get_record(GYM_COLLECTION, "uid", uid)
        validate_existing_log(existing_log=existing_log,
                              current_user=current_user)
        DB.delete_record(GYM_COLLECTION, "uid", uid)
        logger.info(f"Log with UID {uid} deleted by user {current_user.email}")
        return {"message": f"Log with UID {uid} deleted successfully."}
    except Exception as e:
        logger.error(f"Error deleting log with UID {uid}: {e}")
        return {"message": f"An error occurred while deleting the log with UID {uid}."}
