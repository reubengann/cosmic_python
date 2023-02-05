import pytest
import models
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db_tables import metadata
from repo import SqlRepository


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    yield sessionmaker(bind=in_memory_db)()


def test_repository_can_save_a_batch(session):
    batch = models.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = SqlRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
        text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]
