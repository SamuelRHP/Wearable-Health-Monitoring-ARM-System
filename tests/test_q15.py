"""Tests for sim.q15 - Fixed-Point Number Representation and Two's Complement Arithmetic."""

import pytest
import math
from sim.q15 import (
    to_q15,
    from_q15,
    to_twos_complement_16,
    from_twos_complement_16,
    to_hex_16,
    to_hex_12,
    saturating_add_q15,
    multiply_q15,
    adc_to_q15,
    compute_quantization_error,
    Q15_MIN,
    Q15_MAX,
    ADC_12BIT_MIDSCALE,
)


def test_to_q15_basic():
    """Verify standard float to Q15 conversions, including syllabus docstring examples."""
    # 0.75 -> 0x6000 (24576)
    assert to_q15(0.75) == 24576
    assert to_hex_16(to_q15(0.75)) == "0x6000"

    # 0.0 -> 0x0000 (0)
    assert to_q15(0.0) == 0
    assert to_hex_16(to_q15(0.0)) == "0x0000"

    # 0.5 -> 0x4000 (16384)
    assert to_q15(0.5) == 16384
    assert to_hex_16(to_q15(0.5)) == "0x4000"

    # -0.5 -> -16384 (0xC000)
    assert to_q15(-0.5) == -16384
    assert to_hex_16(to_q15(-0.5)) == "0xC000"

    # -1.0 -> 0x8000 (-32768)
    assert to_q15(-1.0) == -32768
    assert to_hex_16(to_q15(-1.0)) == "0x8000"


def test_to_q15_saturation():
    """Verify that inputs outside [-1.0, 0.999969] saturate properly."""
    assert to_q15(1.5) == Q15_MAX
    assert to_q15(2.0) == Q15_MAX
    assert to_q15(-1.5) == Q15_MIN
    assert to_q15(-10.0) == Q15_MIN


def test_from_q15():
    """Verify conversion from Q15 integer back to floating point."""
    assert math.isclose(from_q15(24576), 0.75, abs_tol=1e-7)
    assert math.isclose(from_q15(16384), 0.5, abs_tol=1e-7)
    assert math.isclose(from_q15(0), 0.0, abs_tol=1e-7)
    assert math.isclose(from_q15(-32768), -1.0, abs_tol=1e-7)

    with pytest.raises(ValueError):
        from_q15(32768)
    with pytest.raises(ValueError):
        from_q15(-32769)


def test_twos_complement():
    """Verify two's complement 16-bit encoding and decoding."""
    # -1 in 16-bit two's complement = 0xFFFF
    assert to_twos_complement_16(-1) == 0xFFFF
    assert to_hex_16(-1) == "0xFFFF"
    assert from_twos_complement_16(0xFFFF) == -1

    # -32768 in two's complement = 0x8000
    assert to_twos_complement_16(-32768) == 0x8000
    assert to_hex_16(-32768) == "0x8000"
    assert from_twos_complement_16(0x8000) == -32768

    # 32767 in two's complement = 0x7FFF
    assert to_twos_complement_16(32767) == 0x7FFF
    assert to_hex_16(32767) == "0x7FFF"
    assert from_twos_complement_16(0x7FFF) == 32767


def test_saturating_add_q15():
    """Verify saturating addition behavior at limits and normal ranges."""
    # Normal sum: 0.25 + 0.25 = 0.5
    assert saturating_add_q15(8192, 8192) == 16384

    # Positive saturation: 30000 + 5000 -> 32767
    assert saturating_add_q15(30000, 5000) == Q15_MAX

    # Negative saturation: -30000 + (-5000) -> -32768
    assert saturating_add_q15(-30000, -5000) == Q15_MIN


def test_multiply_q15():
    """Verify Q15 multiplication with right shift by 15.

    Docstring example: 0.5 * 0.5 = 16384 * 16384 >> 15 = 8192 = 0.25
    """
    assert multiply_q15(16384, 16384) == 8192
    assert math.isclose(from_q15(8192), 0.25, abs_tol=1e-7)

    # 0.75 * 0.5 = 0.375
    # 24576 * 16384 >> 15 = 12288 -> 12288 / 32768 = 0.375
    assert multiply_q15(24576, 16384) == 12288
    assert math.isclose(from_q15(12288), 0.375, abs_tol=1e-7)

    # Corner case: -1.0 * -1.0 = +1.0 (saturates to Q15_MAX = 32767)
    assert multiply_q15(-32768, -32768) == Q15_MAX


def test_adc_to_q15():
    """Verify 12-bit ADC [0, 4095] conversion to signed Q15 [-32768, 32767]."""
    # Midscale (2048) -> 0
    assert adc_to_q15(ADC_12BIT_MIDSCALE) == 0
    assert to_hex_12(2048) == "0x800"

    # Minimum ADC code (0) -> -32768 (0x8000)
    assert adc_to_q15(0) == -32768
    assert to_hex_12(0) == "0x000"

    # Maximum ADC code (4095) -> 32752 (0x7FF0)
    assert adc_to_q15(4095) == 32752
    assert to_hex_12(4095) == "0xFFF"

    # Out of range checks
    with pytest.raises(ValueError):
        adc_to_q15(-1)
    with pytest.raises(ValueError):
        adc_to_q15(4096)


def test_quantization_error():
    """Test quantization error calculation across a simulated sinusoidal pulse."""
    floats = [math.sin(2 * math.pi * i / 100) * 0.8 for i in range(100)]
    q15s = [to_q15(f) for f in floats]

    metrics = compute_quantization_error(floats, q15s)
    # The quantization step in Q15 is 1 / 32768 ≈ 3.0517e-5
    # Max error should be strictly <= 0.5 LSB = 0.5 / 32768 ≈ 1.53e-5
    assert metrics["max_absolute_error"] < 2e-5
    assert metrics["rmse"] < 1.5e-5
    assert metrics["snr_db"] > 80.0
