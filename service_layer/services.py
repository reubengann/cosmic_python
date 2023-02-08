from datetime import date
from typing import Optional

from adapters.repository import Repository
from domain import models
from domain.models import OrderLine
from service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date], uow: AbstractUnitOfWork
) -> None:
    with uow:
        uow.batches.add(models.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(order_id: str, sku: str, qty: int, uow: AbstractUnitOfWork):
    line = OrderLine(order_id, sku, qty)

    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = models.allocate_line_to_batches(line, batches)
        # magic
        uow.commit()
    return batchref
