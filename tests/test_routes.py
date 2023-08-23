import pytest
import uuid

from schemas.schema import FastAPIAuth as fauth
from models.gym import ExerciseLogs, RunningExercises, RunningLog, WeightExercises, WeightLog
from fastapi import status
from typing import AsyncIterator
from fastapi.testclient import TestClient
from datetime import timedelta

from db import DB
from main import app

fake_collection = f"fake_{uuid.uuid4()}"


client = TestClient(app)

mock_exerciselogs = ExerciseLogs(
    exercises=[
        RunningLog(
            exercise=RunningExercises.OUTDOOR_RUNNING,
            distance=8,
            duration_in_seconds=3000,
        )
    ],
    user_email="testuser@packt.com"
)


ac_token = fauth().create_access_token(
    data={"sub": "testuser@packt.com"}, expires_delta=timedelta(minutes=15))

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ac_token}"
}


def test_mock_exerciselogs():
    global mock_exerciselogs
    response = client.post("/gym/logs", headers=headers,
                           data=mock_exerciselogs.json())
    assert response.status_code == status.HTTP_200_OK
    mock_exerciselogs = ExerciseLogs.parse_obj(response.json())

    # In Python, the yield keyword is used for writing generator functions,
    # in pytest, the yield can be used to finalize (clean-up)
    # after the fixture code is executed. Pytest's documentation
    # states the following. “Yield” fixtures yield instead of
    # return


def test_get_logs() -> None:
    response = client.get("/gym/logs", headers=headers)
    print(response.status_code, response.text)
    assert response.status_code == status.HTTP_200_OK
    all_uids = [x.get("uid") for x in response.json()]
    assert str(mock_exerciselogs.uid) in all_uids


def test_get_log() -> None:
    url = f"/gym/logs/{str(mock_exerciselogs.uid)}"
    response = client.get(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_update_log() -> None:
    url = f"/gym/logs?uid={str(mock_exerciselogs.uid)}"
    mock_exerciselogs.exercises.append(WeightLog(
        exercise=WeightExercises.BENCH_PRESS,
        sets=2,
        reps=12,
        weight=15,
        duration_in_seconds=1200
    ))
    response = client.patch(
        url, data=mock_exerciselogs.json(), headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_delete_log() -> None:
    test_response = {"message": "Event Get Deleted Successfully."}
    url = f"/gym/logs?uid={mock_exerciselogs.uid}"
    response = client.delete(url, headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
