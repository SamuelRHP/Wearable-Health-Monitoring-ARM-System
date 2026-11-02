"""ARM Cortex-M Thumb execution simulator using the Unicorn Engine.

COA Concept: Hardware Instruction Emulation & Register-Level Trace
------------------------------------------------------------------
This module executes real 16-bit ARM Thumb machine code on the Unicorn Engine
(an instruction set emulator based on QEMU). It emulates an ARM Cortex-M core
executing a 4-sample moving average filter and threshold comparison.

After each instruction step, a hook callback records:
- The instruction assembly mnemonic.
- Low register state: R0 through R7.
- APSR status flags: N, Z, C, V.

The output is compared against a pure Python mathematical reference to guarantee
100% architectural fidelity.

Worked Example for Students:
-----------------------------
Given 4 samples in Q15 format: [1000, 2000, 3000, 4000] and threshold = 2000:
1. Pure Python:
   sum = 1000 + 2000 + 3000 + 4000 = 10000.
   average = 10000 >> 2 = 2500 (Q15 4-tap boxcar filter).
   average > threshold (2500 > 2000) -> Alert = True.
2. Unicorn ARM Execution:
   The Thumb assembly loads each halfword, accumulates in R2, performs ASRS R2, R2, #2,
   compares R2 with R1 (CMP R2, R1), and takes the conditional branch BGT.
   Final registers: R2 = 2500, R0 = 1 (Alert Active).
   Both implementations match bit-for-bit.
"""

from __future__ import annotations
import struct
from typing import Sequence, Any

import unicorn as uc
from unicorn.arm_const import (
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
    UC_ARM_REG_R6,
    UC_ARM_REG_R7,
    UC_ARM_REG_PC,
    UC_ARM_REG_CPSR,
)

# 16-bit Thumb Machine Code (36 bytes, 18 instructions)
THUMB_MACHINE_CODE: bytes = bytes([
    0x02, 0x88,  # 0x00: ldrh r2, [r0, #0]
    0x12, 0xB2,  # 0x02: sxth r2, r2
    0x43, 0x88,  # 0x04: ldrh r3, [r0, #2]
    0x1B, 0xB2,  # 0x06: sxth r3, r3
    0xD2, 0x18,  # 0x08: adds r2, r2, r3
    0x83, 0x88,  # 0x0A: ldrh r3, [r0, #4]
    0x1B, 0xB2,  # 0x0C: sxth r3, r3
    0xD2, 0x18,  # 0x0E: adds r2, r2, r3
    0xC3, 0x88,  # 0x10: ldrh r3, [r0, #6]
    0x1B, 0xB2,  # 0x12: sxth r3, r3
    0xD2, 0x18,  # 0x14: adds r2, r2, r3
    0x92, 0x10,  # 0x16: asrs r2, r2, #2
    0x8A, 0x42,  # 0x18: cmp r2, r1
    0x01, 0xDC,  # 0x1A: bgt alert_high (+2)
    0x00, 0x20,  # 0x1C: movs r0, #0
    0x00, 0xE0,  # 0x1E: b done (+0)
    0x01, 0x20,  # 0x20: movs r0, #1
    0x00, 0xBF,  # 0x22: nop
])

DISASSEMBLY_MAP: dict[int, str] = {
    0x00: "ldrh r2, [r0, #0]",
    0x02: "sxth r2, r2",
    0x04: "ldrh r3, [r0, #2]",
    0x06: "sxth r3, r3",
    0x08: "adds r2, r2, r3",
    0x0A: "ldrh r3, [r0, #4]",
    0x0C: "sxth r3, r3",
    0x0E: "adds r2, r2, r3",
    0x10: "ldrh r3, [r0, #6]",
    0x12: "sxth r3, r3",
    0x14: "adds r2, r2, r3",
    0x16: "asrs r2, r2, #2",
    0x18: "cmp r2, r1",
    0x1A: "bgt alert_high",
    0x1C: "movs r0, #0",
    0x1E: "b done",
    0x20: "movs r0, #1",
    0x22: "nop",
}

CODE_BASE_ADDR: int = 0x10000
DATA_BASE_ADDR: int = 0x20000
MEM_PAGE_SIZE: int = 0x1000


def moving_average_4_python(samples: Sequence[int], threshold: int) -> tuple[int, bool]:
    """Pure Python reference implementation of the 4-sample moving average and threshold compare.

    Args:
        samples: Sequence of 4 signed 16-bit Q15 integers [-32768, 32767].
        threshold: Signed 16-bit Q15 threshold.

    Returns:
        (filtered_average, alert_flag)
    """
    if len(samples) != 4:
        raise ValueError(f"Expected 4 samples, got {len(samples)}")

    # Ensure 16-bit sign interpretation
    signed_samples = [s if s < 0x8000 else s - 0x10000 for s in samples]
    raw_sum = sum(signed_samples)

    # Arithmetic shift right by 2 (preserves sign)
    average = raw_sum >> 2

    # Threshold comparison
    alert = average > threshold
    return average, alert


class ARMEmulator:
    """Manages a persistent Unicorn ARM Cortex-M emulator instance."""

    def __init__(self) -> None:
        self.mu = uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_THUMB)
        self.mu.mem_map(CODE_BASE_ADDR, MEM_PAGE_SIZE)
        self.mu.mem_map(DATA_BASE_ADDR, MEM_PAGE_SIZE)
        self.mu.mem_write(CODE_BASE_ADDR, THUMB_MACHINE_CODE)

    def run(
        self,
        samples: Sequence[int],
        threshold: int,
        trace_steps: bool = True,
    ) -> dict[str, Any]:
        """Execute the routine with the specified 4 samples and threshold."""
        if len(samples) != 4:
            raise ValueError(f"Expected 4 samples, got {len(samples)}")

        # Flush JIT translation block cache so code hooks fire reliably
        self.mu.ctl_flush_tb()

        # Write samples to data memory
        packed = struct.pack("<4h", *samples)
        self.mu.mem_write(DATA_BASE_ADDR, packed)

        # Reset registers
        self.mu.reg_write(UC_ARM_REG_R0, DATA_BASE_ADDR)
        self.mu.reg_write(UC_ARM_REG_R1, threshold & 0xFFFFFFFF)
        self.mu.reg_write(UC_ARM_REG_R2, 0)
        self.mu.reg_write(UC_ARM_REG_R3, 0)
        self.mu.reg_write(UC_ARM_REG_R4, 0)
        self.mu.reg_write(UC_ARM_REG_R5, 0)
        self.mu.reg_write(UC_ARM_REG_R6, 0)
        self.mu.reg_write(UC_ARM_REG_R7, 0)

        steps: list[dict[str, Any]] = []
        hook_handle = None

        if trace_steps:
            def hook_code(uc_eng: uc.Uc, address: int, size: int, user_data: Any) -> None:
                offset = address - CODE_BASE_ADDR
                mnemonic = DISASSEMBLY_MAP.get(offset, f"thumb_0x{offset:02X}")
                cpsr = uc_eng.reg_read(UC_ARM_REG_CPSR)
                steps.append({
                    "instruction": mnemonic,
                    "registers": {
                        "r0": uc_eng.reg_read(UC_ARM_REG_R0),
                        "r1": uc_eng.reg_read(UC_ARM_REG_R1),
                        "r2": uc_eng.reg_read(UC_ARM_REG_R2),
                        "r3": uc_eng.reg_read(UC_ARM_REG_R3),
                        "r4": uc_eng.reg_read(UC_ARM_REG_R4),
                        "r5": uc_eng.reg_read(UC_ARM_REG_R5),
                        "r6": uc_eng.reg_read(UC_ARM_REG_R6),
                        "r7": uc_eng.reg_read(UC_ARM_REG_R7),
                    },
                    "flags": {
                        "N": bool((cpsr >> 31) & 1),
                        "Z": bool((cpsr >> 30) & 1),
                        "C": bool((cpsr >> 29) & 1),
                        "V": bool((cpsr >> 28) & 1),
                    },
                })

            hook_handle = self.mu.hook_add(uc.UC_HOOK_CODE, hook_code)

        # Start emulation
        self.mu.emu_start(CODE_BASE_ADDR | 1, CODE_BASE_ADDR + len(THUMB_MACHINE_CODE))

        if hook_handle is not None:
            self.mu.hook_del(hook_handle)

        raw_r0 = self.mu.reg_read(UC_ARM_REG_R0)
        raw_r2 = self.mu.reg_read(UC_ARM_REG_R2)
        signed_avg = raw_r2 if raw_r2 < 0x80000000 else raw_r2 - 0x100000000
        alert_flag = bool(raw_r0 & 1)

        py_avg, py_alert = moving_average_4_python(samples, threshold)
        matches_python = (signed_avg == py_avg) and (alert_flag == py_alert)

        return {
            "average": signed_avg,
            "alert": alert_flag,
            "steps": steps,
            "matches_python": matches_python,
        }


# Module-level cached emulator instance
_EMULATOR_INSTANCE: ARMEmulator | None = None


def get_arm_emulator() -> ARMEmulator:
    """Return a cached ARMEmulator instance."""
    global _EMULATOR_INSTANCE
    if _EMULATOR_INSTANCE is None:
        _EMULATOR_INSTANCE = ARMEmulator()
    return _EMULATOR_INSTANCE


def execute_moving_average_unicorn(
    samples: Sequence[int],
    threshold: int,
    trace_steps: bool = True,
) -> dict[str, Any]:
    """Execute the ARM Thumb moving average routine on the Unicorn emulator.

    Traces register state (R0-R7) and APSR flags after each instruction step.
    Compares final output with the pure Python reference algorithm.
    """
    emulator = get_arm_emulator()
    return emulator.run(samples, threshold, trace_steps=trace_steps)
