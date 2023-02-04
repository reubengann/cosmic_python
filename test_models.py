from datetime import date

from models import Batch, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 21)
    assert not large_batch.can_allocate(small_line)


def test_can_allocate_if_available_equal_to_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 20)
    assert large_batch.can_allocate(small_line)


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )
