from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.available_quantity = qty

    def allocate(self, line: OrderLine):
        self.available_quantity -= line.qty

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
