"""Tests for sim.alu - 32-bit ALU operations, APSR flags, and conditional branching."""

import pytest
from sim.alu import ALU, APSRFlags, evaluate_condition


def test_alu_add_basic_and_flags():
    """Verify standard addition and flag states."""
    # 5 + 10 = 15: N=0, Z=0, C=0, V=0
    res = ALU.add(5, 10)
    assert res.result == 15
    assert not res.flags.N
    assert not res.flags.Z
    assert not res.flags.C
    assert not res.flags.V

    # Zero flag: 0 + 0 = 0
    res = ALU.add(0, 0)
    assert res.result == 0
    assert res.flags.Z
    assert not res.flags.N


def test_alu_add_overflow_and_carry():
    """Verify signed overflow (V) and unsigned carry (C) flags in ADD."""
    # Unsigned carry: 0xFFFFFFFF + 1 = 0 (carry out = 1)
    res = ALU.add(0xFFFFFFFF, 1)
    assert res.result == 0
    assert res.flags.Z
    assert res.flags.C
    assert not res.flags.V  # Not signed overflow (neg + pos)

    # Signed overflow: 0x7FFFFFFF (max positive) + 1 = 0x80000000 (negative)
    res = ALU.add(0x7FFFFFFF, 1)
    assert res.result == 0x80000000
    assert res.flags.N
    assert res.flags.V  # Pos + Pos = Neg -> Signed Overflow!
    assert not res.flags.C


def test_alu_sub_and_cmp():
    """Verify subtraction and ARM carry/borrow convention:

    In ARM: C = 1 means NO borrow (A >= B unsigned).
            C = 0 means borrow occurred (A < B unsigned).
    """
    # 10 - 5 = 5 (A >= B -> C=1, no borrow)
    res = ALU.sub(10, 5)
    assert res.result == 5
    assert not res.flags.N
    assert not res.flags.Z
    assert res.flags.C  # No borrow
    assert not res.flags.V

    # 5 - 10 = -5 = 0xFFFFFFFB (borrow -> C=0, N=1)
    res = ALU.sub(5, 10)
    assert res.result == 0xFFFFFFFB
    assert res.flags.N
    assert not res.flags.C  # Borrow occurred
    assert not res.flags.V

    # Equal: 10 - 10 = 0 (Z=1, C=1)
    res = ALU.sub(10, 10)
    assert res.result == 0
    assert res.flags.Z
    assert res.flags.C

    # Signed overflow in subtraction:
    # -2147483648 (0x80000000) - 1 = +2147483647 (0x7FFFFFFF) -> V=1
    res = ALU.sub(0x80000000, 1)
    assert res.result == 0x7FFFFFFF
    assert res.flags.V
    assert not res.flags.N


def test_cmp_bpm_threshold_alert_branch():
    """Verify the exact syllabus requirement:

    Show how CMP bpm, threshold drives the alert branch.
    CMP r0 (bpm), r1 (threshold) followed by BGT alert_high.
    """
    # Scenario 1: Tachycardia alert (bpm = 110, threshold = 100)
    flags_tachy = ALU.cmp(110, 100)
    assert not flags_tachy.N
    assert not flags_tachy.Z
    assert flags_tachy.C  # 110 >= 100
    assert not flags_tachy.V
    # BGT condition: Z == 0 and N == V
    assert evaluate_condition("GT", flags_tachy) is True
    assert evaluate_condition("LE", flags_tachy) is False

    # Scenario 2: Normal rhythm (bpm = 75, threshold = 100)
    flags_normal = ALU.cmp(75, 100)
    assert flags_normal.N  # 75 - 100 = -25 (negative)
    assert not flags_normal.Z
    assert not flags_normal.C  # borrow
    assert not flags_normal.V
    # BGT condition is False (N != V: 1 != 0)
    assert evaluate_condition("GT", flags_normal) is False
    assert evaluate_condition("LE", flags_normal) is True
    assert evaluate_condition("LT", flags_normal) is True

    # Scenario 3: At exact threshold boundary (bpm = 100, threshold = 100)
    flags_boundary = ALU.cmp(100, 100)
    assert flags_boundary.Z
    assert evaluate_condition("GT", flags_boundary) is False
    assert evaluate_condition("GE", flags_boundary) is True
    assert evaluate_condition("EQ", flags_boundary) is True


def test_alu_shifts():
    """Verify ASR, LSL, LSR operations."""
    # ASR #2 (division by 4 for 4-sample moving average):
    # 16 >> 2 = 4
    res = ALU.asr(16, 2)
    assert res.result == 4
    assert not res.flags.N
    assert not res.flags.Z

    # Negative ASR preserves sign: -16 (0xFFFFFFF0) >> 2 = -4 (0xFFFFFFFC)
    res = ALU.asr(0xFFFFFFF0, 2)
    assert res.result == 0xFFFFFFFC
    assert res.flags.N

    # LSL #4 (12-bit ADC to 16-bit Q15 hardware shift):
    # 1 << 4 = 16
    res = ALU.lsl(1, 4)
    assert res.result == 16

    # LSR #2 (unsigned shift right):
    # 0x80000000 >> 1 = 0x40000000 (sign bit cleared)
    res = ALU.lsr(0x80000000, 1)
    assert res.result == 0x40000000
    assert not res.flags.N
