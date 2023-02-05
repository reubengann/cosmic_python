from dataclasses import dataclass
from datetime import date
from typing import Optional, Set

class OutOfStock(Exception):
    pass

@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:
    _lines: Set[OrderLine]

    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._lines = set()

    def allocate(self, line: OrderLine):
        if line not in self._lines:
            self._lines.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._lines:
            self._lines.remove(line)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    @property
    def allocated_quantity(self):
        return sum(l.qty for l in self._lines)

    def can_allocate(self, line: OrderLine) -> bool:
        if line.sku != self.sku:
            return False
        return line.qty <= self.available_quantity


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    best = find_best_batch(line, batches)
    if best is None:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
    best.allocate(line)
    return best.reference


def find_best_batch(line: OrderLine, batches: list[Batch]) -> Batch | None:
    best = None
    best_time = date.max
    for batch in batches:
        if not batch.can_allocate(line):
            continue
        if batch.eta is None:
            return batch
        if batch.eta < best_time:
            best = batch
            best_time = batch.eta
    return best

    