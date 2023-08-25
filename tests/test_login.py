import httpx
import pytest
import urllib.parse

from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_sign_new_user() -> None:
    payload = {
        "email": "testuser9@packt.com",
        "password": "test9assword",
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    test_response = {
        "message": "User created successfully"
    }

    response = client.post("/signup", json=payload, headers=headers)
    response_data = response.json()

    print("Checking response:", response_data)

    assert response.status_code == 200


def test_sign_user_in() -> None:
    payload = {
        "username": "testuser11@packt.com",
        "password": "test9assword",
        "is_active": True
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    body = urllib.parse.urlencode(payload)
    response = client.post("/login", data=body, headers=headers)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
