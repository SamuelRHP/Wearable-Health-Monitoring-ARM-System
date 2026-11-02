"""32-bit Arithmetic Logic Unit (ALU) simulator with ARM APSR condition flags.

COA Concept: 32-bit ALU Architecture & Condition Flags (APSR)
--------------------------------------------------------------
The ALU is the computational core of the ARM Cortex-M processor. Every arithmetic
and logical operation computes a 32-bit result and can update the four condition flags
in the Application Program Status Register (APSR):
- N (Negative): Set to 1 if MSB (bit 31) of the result is 1 (result is negative in two's complement).
- Z (Zero): Set to 1 if the 32-bit result is exactly 0x00000000.
- C (Carry):
  * For addition: Set to 1 if an unsigned overflow occurs (carry out of bit 31).
  * For subtraction and CMP (A - B = A + ~B + 1): Set to 1 if NO borrow was required (A >= B unsigned).
  * For shift operations: Holds the last bit shifted out of the operand.
- V (Overflow): Set to 1 if a signed overflow occurs (adding two positives gives a negative,
  or subtracting a negative from a positive gives a negative).

Worked Examples for Students:
-----------------------------
1. Alert Branching with CMP:
   In health monitoring, instantaneous heart rate (bpm) is checked against a safety threshold:
   ARM Assembly:
       CMP   r0, r1       // Compare heart rate (r0) with threshold (r1)
       BGT   alert_high   // Branch if signed greater than (Z == 0 and N == V)

   Scenario A (Tachycardia Alert):
       r0 = 110 bpm, r1 = 100 bpm.
       CMP computes: 110 - 100 = +10.
       Flags: N=0, Z=0, C=1 (no borrow), V=0 (no signed overflow).
       Condition BGT checks: (Z == 0) and (N == V) -> (0 == 0) and (0 == 0) -> TRUE!
       Branch is taken -> Alert triggered.

   Scenario B (Normal Rhythm):
       r0 = 75 bpm, r1 = 100 bpm.
       CMP computes: 75 - 100 = -25 (0xFFFFFFE7 in 32-bit two's complement).
       Flags: N=1 (MSB=1), Z=0, C=0 (borrow occurred), V=0.
       Condition BGT checks: (Z == 0) and (N == V) -> (0 == 0) and (1 == 0) -> FALSE.
       Branch is NOT taken -> Normal monitoring continues.

2. Arithmetic Shift Right (ASRS) in Moving Average:
   To divide a sum of 4 Q15 samples by 4:
       ASR   r0, r0, #2
   Arithmetic shift preserves the sign bit (bit 31) while shifting bits right.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Tuple


MASK_32: int = 0xFFFFFFFF
SIGN_BIT_32: int = 0x80000000


@dataclass(frozen=True)
class APSRFlags:
    """ARM Application Program Status Register (APSR) condition flags."""
    N: bool  # Negative
    Z: bool  # Zero
    C: bool  # Carry / Not Borrow
    V: bool  # Overflow

    def to_dict(self) -> dict[str, bool]:
        """Convert flags to dictionary matching API schema."""
        return {"N": self.N, "Z": self.Z, "C": self.C, "V": self.V}


@dataclass(frozen=True)
class ALUResult:
    """Output of an ALU operation including result and status flags."""
    result: int
    flags: APSRFlags


def evaluate_condition(condition: str, flags: APSRFlags) -> bool:
    """Evaluate an ARM condition code (e.g., 'EQ', 'NE', 'GT', 'LT', 'GE', 'LE').

    COA Concept: Conditional Execution & Branch Decisions.

    Worked Example:
        >>> f = APSRFlags(N=False, Z=False, C=True, V=False)
        >>> evaluate_condition("GT", f)  # Z==0 and N==V
        True
        >>> evaluate_condition("EQ", f)  # Z==1
        False
    """
    cond = condition.upper()
    if cond == "EQ":
        return flags.Z
    elif cond == "NE":
        return not flags.Z
    elif cond == "CS" or cond == "HS":
        return flags.C
    elif cond == "CC" or cond == "LO":
        return not flags.C
    elif cond == "MI":
        return flags.N
    elif cond == "PL":
        return not flags.N
    elif cond == "VS":
        return flags.V
    elif cond == "VC":
        return not flags.V
    elif cond == "HI":
        return flags.C and not flags.Z
    elif cond == "LS":
        return (not flags.C) or flags.Z
    elif cond == "GE":
        return flags.N == flags.V
    elif cond == "LT":
        return flags.N != flags.V
    elif cond == "GT":
        return (not flags.Z) and (flags.N == flags.V)
    elif cond == "LE":
        return flags.Z or (flags.N != flags.V)
    elif cond == "AL":
        return True
    else:
        raise ValueError(f"Unknown ARM condition code: {condition}")


class ALU:
    """Simulated 32-bit Arithmetic Logic Unit conforming to ARM Cortex-M behavior."""

    @staticmethod
    def _is_neg(val_32: int) -> bool:
        return bool(val_32 & SIGN_BIT_32)

    @staticmethod
    def add(a: int, b: int, carry_in: bool = False) -> ALUResult:
        """Perform 32-bit addition: A + B (+ carry_in).

        Computes N, Z, C, V flags.
        """
        a_u = a & MASK_32
        b_u = b & MASK_32
        cin = 1 if carry_in else 0

        raw_sum = a_u + b_u + cin
        res_32 = raw_sum & MASK_32

        n_flag = bool(res_32 & SIGN_BIT_32)
        z_flag = res_32 == 0
        c_flag = raw_sum > MASK_32

        # Signed overflow: operands have same sign, but result has different sign
        a_sign = bool(a_u & SIGN_BIT_32)
        b_sign = bool(b_u & SIGN_BIT_32)
        res_sign = n_flag
        v_flag = (a_sign == b_sign) and (a_sign != res_sign)

        flags = APSRFlags(N=n_flag, Z=z_flag, C=c_flag, V=v_flag)
        return ALUResult(result=res_32, flags=flags)

    @staticmethod
    def sub(a: int, b: int, borrow_in: bool = False) -> ALUResult:
        """Perform 32-bit subtraction: A - B (- borrow_in).

        In ARM architecture: Subtraction is implemented as A + ~B + C.
        C = 1 means NO borrow occurred (A >= B unsigned).
        C = 0 means borrow occurred (A < B unsigned).
        """
        a_u = a & MASK_32
        b_u = b & MASK_32
        # Carry in for subtraction is 1 if NOT borrow
        cin = 0 if borrow_in else 1

        # A + ~B + cin
        not_b = (~b_u) & MASK_32
        raw_sum = a_u + not_b + cin
        res_32 = raw_sum & MASK_32

        n_flag = bool(res_32 & SIGN_BIT_32)
        z_flag = res_32 == 0
        c_flag = raw_sum > MASK_32  # In ARM: C=1 if no borrow, C=0 if borrow

        # Signed overflow for subtraction:
        # A positive, B negative -> result negative (overflow)
        # A negative, B positive -> result positive (underflow)
        a_sign = bool(a_u & SIGN_BIT_32)
        b_sign = bool(b_u & SIGN_BIT_32)
        res_sign = n_flag
        v_flag = (a_sign != b_sign) and (a_sign != res_sign)

        flags = APSRFlags(N=n_flag, Z=z_flag, C=c_flag, V=v_flag)
        return ALUResult(result=res_32, flags=flags)

    @classmethod
    def cmp(cls, a: int, b: int) -> APSRFlags:
        """Perform ARM CMP instruction: computes A - B and updates flags without saving result.

        Worked Example:
            >>> flags = ALU.cmp(110, 100)  # 110 > 100
            >>> flags.N, flags.Z, flags.C, flags.V
            (False, False, True, False)
        """
        sub_res = cls.sub(a, b)
        return sub_res.flags

    @staticmethod
    def asr(a: int, shift: int) -> ALUResult:
        """Perform 32-bit Arithmetic Shift Right (ASR): preserves sign bit.

        COA Concept: Division by powers of two for moving average (ASR #2 = / 4).
        """
        if shift < 0:
            raise ValueError("Shift amount cannot be negative")
        if shift == 0:
            a_u = a & MASK_32
            return ALUResult(
                result=a_u,
                flags=APSRFlags(
                    N=bool(a_u & SIGN_BIT_32),
                    Z=a_u == 0,
                    C=False,
                    V=False,
                ),
            )

        a_u = a & MASK_32
        is_neg = bool(a_u & SIGN_BIT_32)

        if shift >= 32:
            res_32 = MASK_32 if is_neg else 0
            c_flag = is_neg
        else:
            c_flag = bool((a_u >> (shift - 1)) & 1)
            # Python bit shift on signed int preserves sign
            signed_a = a_u if not is_neg else a_u - 0x100000000
            res_32 = (signed_a >> shift) & MASK_32

        n_flag = bool(res_32 & SIGN_BIT_32)
        z_flag = res_32 == 0

        return ALUResult(
            result=res_32,
            flags=APSRFlags(N=n_flag, Z=z_flag, C=c_flag, V=False),
        )

    @staticmethod
    def lsl(a: int, shift: int) -> ALUResult:
        """Perform 32-bit Logical Shift Left (LSL)."""
        if shift < 0:
            raise ValueError("Shift amount cannot be negative")
        if shift == 0:
            a_u = a & MASK_32
            return ALUResult(
                result=a_u,
                flags=APSRFlags(
                    N=bool(a_u & SIGN_BIT_32),
                    Z=a_u == 0,
                    C=False,
                    V=False,
                ),
            )

        a_u = a & MASK_32
        if shift > 32:
            res_32 = 0
            c_flag = False
        elif shift == 32:
            res_32 = 0
            c_flag = bool(a_u & 1)
        else:
            c_flag = bool((a_u >> (32 - shift)) & 1)
            res_32 = (a_u << shift) & MASK_32

        n_flag = bool(res_32 & SIGN_BIT_32)
        z_flag = res_32 == 0
        return ALUResult(
            result=res_32,
            flags=APSRFlags(N=n_flag, Z=z_flag, C=c_flag, V=False),
        )

    @staticmethod
    def lsr(a: int, shift: int) -> ALUResult:
        """Perform 32-bit Logical Shift Right (LSR): shifts in zeroes."""
        if shift < 0:
            raise ValueError("Shift amount cannot be negative")
        if shift == 0:
            a_u = a & MASK_32
            return ALUResult(
                result=a_u,
                flags=APSRFlags(
                    N=bool(a_u & SIGN_BIT_32),
                    Z=a_u == 0,
                    C=False,
                    V=False,
                ),
            )

        a_u = a & MASK_32
        if shift > 32:
            res_32 = 0
            c_flag = False
        elif shift == 32:
            res_32 = 0
            c_flag = bool(a_u & SIGN_BIT_32)
        else:
            c_flag = bool((a_u >> (shift - 1)) & 1)
            res_32 = (a_u >> shift) & MASK_32

        n_flag = bool(res_32 & SIGN_BIT_32)
        z_flag = res_32 == 0
        return ALUResult(
            result=res_32,
            flags=APSRFlags(N=n_flag, Z=z_flag, C=c_flag, V=False),
        )
