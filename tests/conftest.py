import time

import pytest


@pytest.fixture(autouse=True)
def track_performance():
    """Automatically track the performance of tests."""
    start_time = time.perf_counter_ns()
    yield
    duration = (time.perf_counter_ns() - start_time) / 1e9
    if duration > 3.0:  # Test is more than 3 second
        pytest.fail(f"Test too slow: {duration}s")
