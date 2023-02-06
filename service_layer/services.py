import domain.models as models
from domain.models import OrderLine
from adapters.repository import Repository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: Repository, session):
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = models.allocate_line_to_batches(line, batches)
    # magic
    session.commit()
    return batchref
