from dataclasses import dataclass
from datetime import date
from typing import Optional, Set


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
        self._puchased_quantity = qty
        self._lines = set()

    def allocate(self, line: OrderLine):
        if line not in self._lines:
            self._lines.add(line)

    def deallocate(self, line: OrderLine):
        if line not in self._lines:
            raise Exception(
                f"Line with sku {line.sku} cannot be deallocated because it is not in the set"
            )
        self._lines.remove(line)

    @property
    def available_quantity(self) -> int:
        return self._puchased_quantity - sum(l.qty for l in self._lines)

    def can_allocate(self, line: OrderLine) -> bool:
        if line.sku != self.sku:
            return False
        return line.qty <= self.available_quantity


def allocate(line: OrderLine, batches: list[Batch]):
    best = find_best_batch(line, batches)
    best.allocate(line)


def find_best_batch(line: OrderLine, batches: list[Batch]) -> Batch:
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
    if best is None:
        raise Exception(f"No batch with SKU {line.sku}")
    return best
