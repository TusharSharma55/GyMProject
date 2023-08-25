from fastapi.testclient import TestClient
import pytest
from main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)
