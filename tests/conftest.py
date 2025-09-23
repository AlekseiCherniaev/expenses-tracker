import time
from uuid import uuid4, UUID

import pytest
from pytest_asyncio import fixture


@fixture(autouse=True)
def track_performance():
    """Automatically track the performance of tests."""
    start_time = time.perf_counter_ns()
    yield
    duration = (time.perf_counter_ns() - start_time) / 1e9
    if duration > 3.0:  # Test is more than 3 second
        pytest.fail(f"Test too slow: {duration}s")


@fixture(autouse=True)
def random_uuid() -> UUID:
    return uuid4()
