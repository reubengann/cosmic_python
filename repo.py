from abc import ABC, abstractmethod
import models


class Repository(ABC):
    @abstractmethod
    def add(self, batch: models.Batch):
        raise NotImplementedError

    @abstractmethod
    def get(self, reference) -> models.Batch:
        raise NotImplementedError


class SqlRepository(Repository):
    def __init__(self, session) -> None:
        self.session = session

    def add(self, batch: models.Batch):
        self.session.add(batch)

    def get(self, reference) -> models.Batch:
        raise NotImplementedError
