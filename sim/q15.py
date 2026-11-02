"""Fixed-point number representation (Q15 format) and two's complement arithmetic.

COA Concept: Number Representation & Fixed-Point Arithmetic
-----------------------------------------------------------
Microcontrollers without a hardware Floating Point Unit (FPU), such as ARM Cortex-M0/M0+
and baseline Cortex-M3/M4 cores in low-power wearables, perform physiological signal
filtering using fixed-point arithmetic. Fixed-point representation uses standard integer
registers and ALU hardware while assuming a fixed implicit binary point.

In the Q15 format (also known as 1.15 format):
- 1 sign bit (bit 15) represents the sign (+ / -).
- 15 fractional bits (bits 14 to 0) represent values in fractional increments of 2^(-15).
- Numerical range: -1.0 <= x <= 1.0 - 2^(-15)  [-1.0 to +0.999969482421875].
- Integer storage: -32768 (0x8000) to +32767 (0x7FFF).

Worked Examples for Students:
-----------------------------
1. Converting float 0.75 to Q15:
   0.75 * 32768 = 24576 = 0x6000.
2. Q15 Multiplication (0.5 * 0.5 = 0.25):
   0.5 in Q15 = 16384 (0x4000).
   Multiplying two 16-bit numbers produces a 32-bit product:
   16384 * 16384 = 268435456 (2.30 format).
   Shift right by 15 bits to return to 1.15 format:
   268435456 >> 15 = 8192 (0x2000).
   Converting 8192 back to float: 8192 / 32768.0 = 0.25.
3. Two's complement representation:
   In 16-bit two's complement, -1 is stored as 0xFFFF:
   -1 & 0xFFFF = 65535 = 0xFFFF.
   -32768 (the minimum Q15 value) is stored as 0x8000.
4. Converting a 12-bit unsigned ADC reading to signed Q15:
   A 12-bit ADC produces integers from 0 to 4095. With midscale at 2048:
   centered_adc = adc_sample - 2048  (range -2048 to +2047).
   In hardware, an ARM core shifts left by 4 bits (LSL #4):
   (-2048) << 4 = -32768 (0x8000 = -1.0).
   (+2047) << 4 = +32752 (0x7FF0 = +0.99951).
"""

from __future__ import annotations
import math
from typing import Sequence, Tuple


# Fixed-point constant definitions
Q15_MIN: int = -32768   # 0x8000 (-1.0 in float)
Q15_MAX: int = 32767    # 0x7FFF (+0.999969482421875 in float)
Q15_SCALE: float = 32768.0
ADC_12BIT_MAX: int = 4095
ADC_12BIT_MIDSCALE: int = 2048


def to_q15(val: float) -> int:
    """Convert an IEEE 754 floating-point number to signed Q15 fixed-point integer.

    COA Concept: Quantization & Fixed-Point Conversion.
    Rounds to nearest integer and saturates to [Q15_MIN, Q15_MAX].

    Worked Example:
        >>> to_q15(0.75)
        24576
        >>> hex(to_q15(0.75))
        '0x6000'
        >>> to_q15(1.5)  # Saturates at maximum Q15
        32767
    """
    scaled = round(val * Q15_SCALE)
    if scaled > Q15_MAX:
        return Q15_MAX
    if scaled < Q15_MIN:
        return Q15_MIN
    return int(scaled)


def from_q15(val: int) -> float:
    """Convert a signed Q15 fixed-point integer back to an IEEE 754 floating-point number.

    COA Concept: Fixed-Point De-quantization.

    Worked Example:
        >>> from_q15(24576)
        0.75
        >>> from_q15(-32768)
        -1.0
        >>> from_q15(8192)
        0.25
    """
    if val > Q15_MAX or val < Q15_MIN:
        raise ValueError(
            f"Value {val} is outside valid 16-bit Q15 range [{Q15_MIN}, {Q15_MAX}]"
        )
    return val / Q15_SCALE


def to_twos_complement_16(val: int) -> int:
    """Convert a signed integer to an unsigned 16-bit two's complement integer (0x0000 to 0xFFFF).

    COA Concept: Two's Complement Integer Representation.
    In two's complement, negative numbers are represented by taking the bitwise
    NOT and adding 1, equivalent to (2^16 + val) for negative values.

    Worked Example:
        >>> to_twos_complement_16(-1)
        65535
        >>> hex(to_twos_complement_16(-1))
        '0xffff'
        >>> hex(to_twos_complement_16(-32768))
        '0x8000'
        >>> hex(to_twos_complement_16(24576))
        '0x6000'
    """
    return val & 0xFFFF


def from_twos_complement_16(val: int) -> int:
    """Interpret an unsigned 16-bit integer as a signed two's complement integer.

    COA Concept: Sign Extension & Two's Complement Decoding.
    If the most significant bit (bit 15) is 1, the value is negative.

    Worked Example:
        >>> from_twos_complement_16(0xFFFF)
        -1
        >>> from_twos_complement_16(0x8000)
        -32768
        >>> from_twos_complement_16(0x6000)
        24576
    """
    val_16 = val & 0xFFFF
    if val_16 & 0x8000:
        return val_16 - 0x10000
    return val_16


def to_hex_16(val: int) -> str:
    """Format a 16-bit integer as an uppercase 4-digit hexadecimal string (0xXXXX).

    Worked Example:
        >>> to_hex_16(-1)
        '0xFFFF'
        >>> to_hex_16(24576)
        '0x6000'
    """
    return f"0x{to_twos_complement_16(val):04X}"


def to_hex_12(val: int) -> str:
    """Format a 12-bit ADC integer as an uppercase 3-digit hexadecimal string (0xXXX).

    Worked Example:
        >>> to_hex_12(4095)
        '0xFFF'
        >>> to_hex_12(2048)
        '0x800'
    """
    return f"0x{val & 0xFFF:03X}"


def saturating_add_q15(a: int, b: int) -> int:
    """Perform saturating addition of two signed Q15 integers.

    COA Concept: Saturating Arithmetic in Digital Signal Processors (ARM QADD).
    Standard integer addition wraps around on overflow (e.g. 32767 + 1 = -32768),
    which produces catastrophic audible/visible audio and sensor glitches.
    Saturating addition clamps the result to the representable boundary.

    Worked Example:
        >>> saturating_add_q15(30000, 5000)  # Standard sum is 35000 (overflows 16-bit signed)
        32767
        >>> saturating_add_q15(-30000, -5000) # Underflows
        -32768
        >>> saturating_add_q15(8192, 8192)    # 0.25 + 0.25 = 0.5 (16384)
        16384
    """
    res = a + b
    if res > Q15_MAX:
        return Q15_MAX
    if res < Q15_MIN:
        return Q15_MIN
    return res


def multiply_q15(a: int, b: int) -> int:
    """Multiply two signed Q15 numbers and shift right by 15 bits.

    COA Concept: Fixed-point Multiplication (ARM SMULBB / ASR #15).
    Multiplying two 1.15 numbers produces a 2.30 product (30 fractional bits).
    Shifting right by 15 bits aligns the product back into the 1.15 format.
    The single corner case (-1.0 * -1.0) equals +1.0, which cannot be represented
    in Q15 and saturates to 0x7FFF (32767).

    Worked Example:
        0.5 * 0.5 = 0.25
        16384 * 16384 = 268435456
        268435456 >> 15 = 8192 (0x2000 = 0.25 in float).
        >>> multiply_q15(16384, 16384)
        8192
        >>> multiply_q15(-32768, -32768)  # -1.0 * -1.0 -> saturates to +0.99997
        32767
    """
    # 32-bit signed product (2.30 format)
    prod = a * b
    # Arithmetic shift right by 15
    res = prod >> 15
    if res > Q15_MAX:
        return Q15_MAX
    if res < Q15_MIN:
        return Q15_MIN
    return res


def adc_to_q15(adc_val: int, midscale: int = ADC_12BIT_MIDSCALE) -> int:
    """Convert an unsigned 12-bit ADC code [0, 4095] to a signed Q15 integer [-32768, 32767].

    COA Concept: Sensor Data Normalization & Hardware Bit-Shifting (LSL #4).
    The sensor frontend provides a 12-bit unsigned code. In embedded systems,
    subtracting midscale and shifting left by 4 bits converts 12-bit signed
    integers directly to 16-bit format without expensive hardware division:
        (adc_val - 2048) << 4

    Worked Example:
        >>> adc_to_q15(2048)   # Midscale (0 V differential) -> 0.0
        0
        >>> adc_to_q15(4095)   # Full-scale positive
        32752
        >>> adc_to_q15(0)      # Full-scale negative -> -32768
        -32768
    """
    if adc_val < 0 or adc_val > ADC_12BIT_MAX:
        raise ValueError(
            f"ADC reading {adc_val} is outside valid 12-bit range [0, {ADC_12BIT_MAX}]"
        )
    centered = adc_val - midscale
    # Hardware shift: 12-bit signed to 16-bit signed
    q15_val = centered << 4
    if q15_val > Q15_MAX:
        return Q15_MAX
    if q15_val < Q15_MIN:
        return Q15_MIN
    return q15_val


def compute_quantization_error(
    float_samples: Sequence[float],
    q15_samples: Sequence[int],
) -> dict[str, float]:
    """Quantify the error introduced by Q15 fixed-point representation vs IEEE 754 double precision.

    Returns:
        A dictionary containing:
        - max_absolute_error: maximum |float - from_q15(q15)|
        - mean_absolute_error: average |float - from_q15(q15)|
        - rmse: root mean squared error
        - snr_db: signal-to-quantization-noise ratio in decibels (approx 6.02 * 15 = 90.3 dB)
    """
    if len(float_samples) != len(q15_samples):
        raise ValueError("Sample arrays must have the same length")
    if len(float_samples) == 0:
        return {
            "max_absolute_error": 0.0,
            "mean_absolute_error": 0.0,
            "rmse": 0.0,
            "snr_db": 0.0,
        }

    errors = []
    signal_sq = 0.0
    noise_sq = 0.0

    for f_val, q_val in zip(float_samples, q15_samples):
        reconstructed = from_q15(q_val)
        err = abs(f_val - reconstructed)
        errors.append(err)
        signal_sq += f_val * f_val
        noise_sq += err * err

    max_err = max(errors)
    mean_err = sum(errors) / len(errors)
    rmse = math.sqrt(sum(e * e for e in errors) / len(errors))

    if noise_sq > 0:
        snr_db = 10.0 * math.log10(signal_sq / noise_sq) if signal_sq > 0 else 0.0
    else:
        snr_db = float("inf")

    return {
        "max_absolute_error": max_err,
        "mean_absolute_error": mean_err,
        "rmse": rmse,
        "snr_db": snr_db,
    }
