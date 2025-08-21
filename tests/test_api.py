import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.text == "ok"


def test_exchanges(client):
    r = client.get("/exchanges")
    assert r.status_code == 200
