import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters.orm import metadata


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///unittest.db")
    metadata.create_all(engine)
    yield engine
    metadata.drop_all(engine)


@pytest.fixture
def session(in_memory_db):
    yield sessionmaker(bind=in_memory_db)()


@pytest.fixture
def session_factory(in_memory_db):
    yield sessionmaker(bind=in_memory_db)


@pytest.fixture
def disk_session(test_db):
    yield sessionmaker(bind=test_db)()


@pytest.fixture
def disk_session_factory(test_db):
    yield sessionmaker(bind=test_db)
