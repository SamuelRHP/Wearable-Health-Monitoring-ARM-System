# ARM Cortex-M Thumb Assembly Routine: 4-Sample Moving Average & Threshold Compare

## 1. COA Architectural Purpose
In low-power wearable biomedical systems (e.g., smart bands, continuous ECG/PPG monitors), signal processing must be executed with minimal energy. The ARM Cortex-M architecture provides compact 16-bit **Thumb** instructions that offer high code density while operating directly on standard registers ($R0$ to $R7$).

This routine executes a classical **4-sample Finite Impulse Response (FIR) boxcar filter** (moving average):
$$\text{Average} = \frac{\sum_{i=0}^{3} \text{sample}[i]}{4}$$
In binary arithmetic, dividing by $4 = 2^2$ is executed via a single-cycle **Arithmetic Shift Right by 2 (`ASRS r2, r2, #2`)**, which preserves the two's complement sign bit.

---

## 2. Machine Code Generation & Opcode Mapping Table

The assembly instructions were translated to 16-bit Thumb machine code in accordance with the **ARMv7-M Architecture Reference Manual**:

| Offset | Assembly Instruction | Hex Opcode | Little-Endian Bytes | Thumb Binary Encoding | Architectural Operation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x00` | `ldrh r2, [r0, #0]` | `0x8802` | `0x02, 0x88` | `10001 00000 000 010` | Load 16-bit halfword from `[r0 + 0]` into `r2` |
| `0x02` | `sxth r2, r2` | `0xB212` | `0x12, 0xB2` | `1011 0010 00 010 010` | Sign-extend bit 15 across bits [31:16] |
| `0x04` | `ldrh r3, [r0, #2]` | `0x8843` | `0x43, 0x88` | `10001 00001 000 011` | Load 16-bit halfword from `[r0 + 2]` into `r3` |
| `0x06` | `sxth r3, r3` | `0xB21B` | `0x1B, 0xB2` | `1011 0010 00 011 011` | Sign-extend bit 15 across bits [31:16] |
| `0x08` | `adds r2, r2, r3` | `0x18D2` | `0xD2, 0x18` | `0001 100 011 010 010` | Accumulate: `r2 = r2 + r3` |
| `0x0A` | `ldrh r3, [r0, #4]` | `0x8883` | `0x83, 0x88` | `10001 00010 000 011` | Load 16-bit halfword from `[r0 + 4]` into `r3` |
| `0x0C` | `sxth r3, r3` | `0xB21B` | `0x1B, 0xB2` | `1011 0010 00 011 011` | Sign-extend bit 15 across bits [31:16] |
| `0x0E` | `adds r2, r2, r3` | `0x18D2` | `0xD2, 0x18` | `0001 100 011 010 010` | Accumulate: `r2 = r2 + r3` |
| `0x10` | `ldrh r3, [r0, #6]` | `0x88C3` | `0xC3, 0x88` | `10001 00011 000 011` | Load 16-bit halfword from `[r0 + 6]` into `r3` |
| `0x12` | `sxth r3, r3` | `0xB21B` | `0x1B, 0xB2` | `1011 0010 00 011 011` | Sign-extend bit 15 across bits [31:16] |
| `0x14` | `adds r2, r2, r3` | `0x18D2` | `0xD2, 0x18` | `0001 100 011 010 010` | Accumulate: `r2 = r2 + r3` |
| `0x16` | `asrs r2, r2, #2` | `0x1092` | `0x92, 0x10` | `0001 0 00010 010 010` | Divide sum by 4: `r2 = r2 >> 2` |
| `0x18` | `cmp r2, r1` | `0x428A` | `0x8A, 0x42` | `0100 0010 10 001 010` | Compute `r2 - r1` to set APSR flags ($N, Z, C, V$) |
| `0x1A` | `bgt +2 (0x20)` | `0xDC01` | `0x01, 0xDC` | `1101 1100 00000001` | Branch to `alert_high` if $Z=0$ and $N=V$ |
| `0x1C` | `movs r0, #0` | `0x2000` | `0x00, 0x20` | `0010 0 000 00000000` | Set alert output = 0 (Normal) |
| `0x1E` | `b +0 (0x22)` | `0xE000` | `0x00, 0xE0` | `1110 0 00000000000` | Unconditional branch to `done` |
| `0x20` | `movs r0, #1` | `0x2001` | `0x01, 0x20` | `0010 0 000 00000001` | Set alert output = 1 (Tachycardia / Alert) |
| `0x22` | `nop` | `0xBF00` | `0x00, 0xBF` | `1011 1111 0000 0000` | No Operation (Pipeline termination) |

Total binary size: 36 bytes (18 Thumb instructions).

---

## 3. Disassembly & Manual Assembly Verification

The assembly file can be assembled with GNU ARM Toolchain (`arm-none-eabi-as`) via:
```bash
arm-none-eabi-as -mcpu=cortex-m4 -mthumb asm/moving_average.s -o asm/moving_average.o
arm-none-eabi-objdump -d asm/moving_average.o
```
The exact byte array is hardcoded into `sim/arm_routine.py` and directly executed in the Unicorn emulator (`UC_ARCH_ARM`, `UC_MODE_THUMB`).
