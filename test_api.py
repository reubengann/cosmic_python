from datetime import date
import uuid
import pytest
from models import Batch
from repository import SqlRepository
from the_api import app, get_session

from fastapi.testclient import TestClient


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name: str | int = ""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


def test_happy_path_returns_201_and_allocated_batch(disk_session):
    app.dependency_overrides[get_session] = lambda: disk_session
    client = TestClient(app)

    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    repo = SqlRepository(disk_session)
    repo.add(Batch(laterbatch, sku, 100, date(2011, 1, 2)))
    repo.add(Batch(earlybatch, sku, 100, date(2011, 1, 1)))
    repo.add(Batch(otherbatch, othersku, 100, None))
    disk_session.commit()
    data = {"order_id": random_orderid(), "sku": sku, "qty": 3}
    r = client.post("/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch
