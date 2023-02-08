import uuid
from datetime import date

from fastapi.testclient import TestClient

from adapters.repository import SqlRepository
from domain.models import Batch
from entrypoints.the_api import app, get_session


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name: str | int = ""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name: str | int = ""):
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


def test_unhappy_path_returns_400_and_error_message(disk_session):
    app.dependency_overrides[get_session] = lambda: disk_session
    client = TestClient(app)
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"order_id": orderid, "sku": unknown_sku, "qty": 20}
    r = client.post("/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["detail"] == f"Invalid sku {unknown_sku}"


def test_allocations_are_persisted(disk_session):
    app.dependency_overrides[get_session] = lambda: disk_session
    client = TestClient(app)

    sku = random_sku()
    batch1, batch2 = random_batchref(1), random_batchref(2)
    order1, order2 = random_orderid(1), random_orderid(2)
    repo = SqlRepository(disk_session)
    repo.add(Batch(batch1, sku, 10, date(2011, 1, 1)))
    repo.add(Batch(batch2, sku, 10, date(2011, 1, 2)))
    disk_session.commit()
    line1 = {"order_id": order1, "sku": sku, "qty": 10}
    line2 = {"order_id": order2, "sku": sku, "qty": 10}

    # first order uses up all stock in batch 1
    r = client.post(f"/allocate", json=line1)
    assert r.status_code == 201
    assert r.json()["batchref"] == batch1

    # second order should go to batch 2
    r = client.post(f"/allocate", json=line2)
    assert r.status_code == 201
    assert r.json()["batchref"] == batch2


def test_400_message_for_out_of_stock(disk_session):
    app.dependency_overrides[get_session] = lambda: disk_session
    client = TestClient(app)
    sku, small_batch, large_order = random_sku(), random_batchref(), random_orderid()
    repo = SqlRepository(disk_session)
    repo.add(Batch(small_batch, sku, 10, date(2011, 1, 1)))
    disk_session.commit()
    data = {"order_id": large_order, "sku": sku, "qty": 20}
    r = client.post(f"/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["detail"] == f"Out of stock for sku {sku}"


def test_add_batch_works(disk_session):
    app.dependency_overrides[get_session] = lambda: disk_session
    repo = SqlRepository(disk_session)
    client = TestClient(app)
    sku = random_sku()
    batch1 = random_batchref(1)
    data = {"ref": batch1, "sku": sku, "qty": 10, "date": str(date(2011, 1, 1))}
    r = client.post(f"/batch", json=data)
    assert r.status_code == 201
    assert len(repo.list()) == 1
