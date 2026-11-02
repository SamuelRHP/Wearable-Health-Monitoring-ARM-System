# Microarchitecture & Signal Path Specification

**Project:** Wearable Health-Monitoring ARM System  
**Student:** Samuel Rohlupuia  
**System Class:** Low-Power Embedded Biomedical Monitor (Simulation Core)

---

## 1. End-to-End Signal Path Architecture

The diagram below details the data flow from physical physiological sensors, through serial interconnects, into fixed-point quantization, through the ARM Cortex-M computational core and cache hierarchy, to output telemetry and power management.

```mermaid
flowchart TD
    subgraph SENSORS ["1. Data Acquisition (Physiological Sensors)"]
        BIDMC["PhysioNet BIDMC Dataset (125 Hz)<br/>Real clinical PLETH (PPG) waveform<br/>(ODC-By 1.0 Licence)"] --> RAW_ADC["12-bit ADC Model<br/>Input range: 0 to 4095<br/>Midscale: 2048 (0 V AC)"]
        SYNTH["Synthetic Generator (Fallback)<br/>Pulse + Dicrotic Notch + Wander"] --> RAW_ADC
    end

    subgraph SERIAL_IN ["2. Sensor Interconnect (I2C Master/Slave)"]
        RAW_ADC --> I2C_BUS["I2C Serial Bus Model<br/>100 kHz Standard Mode / 400 kHz Fast<br/>Transaction: START + Addr + Reg + Sr + Data(2B) + STOP<br/>Total: 48 Clock Cycles (480 us @ 100 kHz)"]
    end

    subgraph NUM_REPR ["3. Number Representation (Hardware Normalization)"]
        I2C_BUS --> Q15_CONV["Signed Q15 Fixed-Point (1.15 Format)<br/>Hardware shift: (ADC - 2048) << 4<br/>Dynamic range: -1.0 <= x <= +0.99997<br/>Storage: 0x8000 (-32768) to 0x7FFF (+32767)"]
    end

    subgraph MEMORY_CORE ["4. ARM Processing & Memory Subsystem"]
        Q15_CONV --> CIRC_BUF["SRAM Circular Sample Buffer<br/>16-bit halfword accesses"]
        CIRC_BUF --> CACHE_SIM["Cache Memory Hierarchy<br/>Configurable 4 KB Direct-Mapped / Set-Associative<br/>16-byte lines: 4 offset bits, 8 index bits, 20 tag bits<br/>AMAT = Hit Time + (Miss Rate x Miss Penalty)"]
        
        CIRC_BUF --> THUMB_CORE["ARM Cortex-M Thumb Core (Unicorn)<br/>16-bit Thumb Assembly Routine:<br/>- 4x LDRH & SXTH (Sign-extend to 32 bits)<br/>- 3x ADDS (Accumulate sum)<br/>- 1x ASRS #2 (Arithmetic shift right / 4)<br/>- 1x CMP r2, r1 (Compare with threshold)<br/>- 1x BGT (Conditional branch)"]
        
        THUMB_CORE --> ALU_SIM["Simulated 32-bit ALU<br/>Computes APSR condition flags:<br/>N (Negative), Z (Zero), C (Carry), V (Overflow)"]
    end

    subgraph OUTPUT_POWER ["5. Output Telemetry & Energy Management"]
        ALU_SIM --> ALERT_LOGIC["Physiological Alert Logic<br/>Tachycardia: BPM > Threshold<br/>Condition: Z == 0 and N == V"]
        
        ALERT_LOGIC --> UART_BUS["UART Telemetry Link<br/>115,200 baud, 8-N-1 (10 bits/frame)<br/>8-byte health telemetry packet @ 125 Hz<br/>Throughput: 1000 B/s (8.68% Bus Utilisation)"]
        
        THUMB_CORE --> DUTY_ENERGY["Duty-Cycle Energy Model<br/>I_avg = I_active * D + I_sleep * (1 - D)<br/>Run (8.4 mA) vs Stop 2 (1.2 uA)<br/>Estimated Savings: ~94.99%"]
    end
```

---

## 2. Subsystem Architectural Breakdown

### A. Number Representation (`sim/q15.py`)
- **Format:** Signed fractional Q15 (1 sign bit, 15 fractional bits).
- **Embedded Justification:** ARM Cortex-M0/M0+/M3 cores lack hardware double-precision FPUs. Fixed-point integer arithmetic saves silicon area and reduces dynamic switching power by avoiding floating-point emulation libraries.
- **Conversion Math:**
  $$x_{Q15} = (ADC - 2048) \ll 4$$
  This operation converts a 12-bit signed offset directly into a 16-bit signed integer using a single ARM `LSL #4` instruction without software division.

### B. Serial Interconnects (`sim/uart.py`, `sim/i2c.py`)
- **I2C Bus:** Synchronous 2-wire serial protocol for sensor communication. Reading a 2-byte sample requires 48 clock cycles ($480\,\mu\text{s}$ at 100 kHz). At 125 Hz, bus utilization is $6.0\%$.
- **UART Link:** Asynchronous serial protocol for streaming telemetry to a companion device or Bluetooth LE module. At 115200 baud with 8-N-1 framing (10 bits per byte), maximum channel capacity is $11,520\text{ bytes/s}$. An 8-byte health packet at 125 Hz utilizes $8.68\%$ of the bandwidth.

### C. 32-bit ALU & Condition Flags (`sim/alu.py`)
- Simulates standard ARM 32-bit integer arithmetic (`ADD`, `SUB`, `CMP`, `ASR`, `LSL`, `LSR`).
- Generates all four ARM status flags in the Application Program Status Register (APSR):
  - $N$ (Negative): Result bit 31 is 1.
  - $Z$ (Zero): Result is exactly 0.
  - $C$ (Carry): Unsigned carry out (ADD) or NO borrow (SUB/CMP).
  - $V$ (Overflow): Signed overflow between operand signs and result sign.
- Evaluates condition codes (`GT`, `LT`, `GE`, `LE`, `EQ`, `NE`) to execute conditional branch instructions.

### D. ARM Cortex-M Core (`asm/moving_average.s`, `sim/arm_routine.py`)
- Executes real 16-bit Thumb machine code inside the Unicorn emulator (`UC_ARCH_ARM`, `UC_MODE_THUMB`).
- Implements a 4-sample boxcar FIR filter:
  $$\text{Average} = \left(\sum_{i=0}^3 \text{sample}[i]\right) \gg 2$$
- Validated instruction-by-instruction with register traces ($R0-R7$, $APSR$) against pure Python.

### E. Cache Memory Hierarchy (`sim/cache.py`)
- Direct-mapped and set-associative cache simulator.
- Partitions 32-bit addresses into Offset, Index, and Tag fields.
- Calculates Average Memory Access Time ($AMAT$):
  $$AMAT = t_{\text{hit}} + (\text{Miss Rate} \times t_{\text{miss}})$$

### F. Duty-Cycle Energy Model (`sim/energy.py`)
- Models power states: Active Run Mode vs Low-Power Sleep (Stop 2).
- Calculated as:
  $$I_{\text{avg}} = I_{\text{active}} \cdot D + I_{\text{sleep}} \cdot (1 - D)$$
- Strictly labeled with `PLACEHOLDER: true` and visible warnings pending student datasheet selection.
