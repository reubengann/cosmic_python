from datetime import date
from typing import Optional
import domain.models as models
from domain.models import OrderLine
from adapters.repository import Repository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: Optional[date],
    repo: Repository,
    session,
) -> None:
    repo.add(models.Batch(ref, sku, qty, eta))
    session.commit()


def allocate(order_id: str, sku: str, qty: int, repo: Repository, session):
    line = OrderLine(order_id, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = models.allocate_line_to_batches(line, batches)
    # magic
    session.commit()
    return batchref
