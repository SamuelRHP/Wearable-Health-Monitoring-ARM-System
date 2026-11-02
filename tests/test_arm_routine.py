"""Tests for sim.arm_routine - ARM Thumb Execution in Unicorn vs Python Reference."""

import random
import pytest
from sim.arm_routine import (
    moving_average_4_python,
    execute_moving_average_unicorn,
)


def test_python_moving_average_basic():
    """Verify hand-calculated moving average and threshold compare in Python."""
    # Positive average: sum(1000, 2000, 3000, 4000) = 10000 -> 10000 >> 2 = 2500
    avg, alert = moving_average_4_python([1000, 2000, 3000, 4000], threshold=2000)
    assert avg == 2500
    assert alert is True

    # Alert condition false: threshold = 3000
    avg, alert = moving_average_4_python([1000, 2000, 3000, 4000], threshold=3000)
    assert avg == 2500
    assert alert is False

    # Negative average: sum(-1000, -2000, -3000, -4000) = -10000 -> -10000 >> 2 = -2500
    avg, alert = moving_average_4_python([-1000, -2000, -3000, -4000], threshold=-3000)
    assert avg == -2500
    assert alert is True


def test_unicorn_emulation_matches_python_basic():
    """Verify that Unicorn emulation produces identical results to Python reference."""
    # Positive alert scenario
    res = execute_moving_average_unicorn([1000, 2000, 3000, 4000], threshold=2000)
    assert res["average"] == 2500
    assert res["alert"] is True
    assert res["matches_python"] is True

    # Negative alert scenario
    res_neg = execute_moving_average_unicorn([-1000, -2000, -3000, -4000], threshold=-3000)
    assert res_neg["average"] == -2500
    assert res_neg["alert"] is True
    assert res_neg["matches_python"] is True

    # Normal non-alert scenario
    res_norm = execute_moving_average_unicorn([500, 600, 700, 800], threshold=1000)
    assert res_norm["average"] == 650
    assert res_norm["alert"] is False
    assert res_norm["matches_python"] is True


def test_unicorn_step_trace():
    """Verify that step-by-step register tracing records instructions and register changes."""
    res = execute_moving_average_unicorn([1000, 2000, 3000, 4000], threshold=2000)
    steps = res["steps"]
    assert len(steps) > 10

    # First step should be ldrh r2, [r0, #0]
    first_step = steps[0]
    assert "ldrh" in first_step["instruction"]
    assert "registers" in first_step
    assert "flags" in first_step
    assert set(first_step["registers"].keys()) == {f"r{i}" for i in range(8)}
    assert set(first_step["flags"].keys()) == {"N", "Z", "C", "V"}


def test_unicorn_vs_python_random_vectors():
    """Automated Verification Suite: Test 500 randomized Q15 vectors.

    Asserts 100% exact match on both filtered sample and alert decision.
    """
    random.seed(42)
    for _ in range(500):
        # Generate 4 random signed 16-bit Q15 samples
        samples = [random.randint(-30000, 30000) for _ in range(4)]
        threshold = random.randint(-20000, 20000)

        res = execute_moving_average_unicorn(samples, threshold)
        assert res["matches_python"] is True
