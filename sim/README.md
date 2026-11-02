# Simulation Core (`sim/`)

This directory houses the standalone, importable Python simulation core for the Wearable Health-Monitoring ARM System.

## Architecture
The simulation core is strictly decoupled from the web framework. Every module can be imported and executed in independent Python scripts, headless batch jobs, or automated testing environments without starting the FastAPI web server.

---

## File Manifest & COA Concepts

| File | Purpose | COA Concept Demonstrated | Worked Example / Key Formula | Test File |
| :--- | :--- | :--- | :--- | :--- |
| `q15.py` | Q15 fixed-point and two's complement conversion | **Number Representation & Arithmetic** | $0.75 \to \text{0x6000}$<br>$0.5 \times 0.5 = 16384 \times 16384 \gg 15 = 8192 = 0.25$<br>$-1 = \text{0xFFFF}$ | `tests/test_q15.py` |
| `uart.py` | UART 8-N-1 framing and timing | **Asynchronous Serial Interconnect** | 115200 baud, 10 bits/B = 11520 B/s.<br>8B @ 100 Hz = 800 B/s (6.94% utilisation) | `tests/test_uart.py` |
| `i2c.py` | I2C transaction timing and state machine | **Synchronous 2-Wire Serial Bus** | 2-byte read = 48 clock cycles.<br>$480\,\mu\text{s}$ @ 100 kHz (6.0% utilisation @ 125 Hz) | `tests/test_i2c.py` |
| `alu.py` | 32-bit ALU with ARM APSR flags ($N, Z, C, V$) | **ALU & Condition Code Logic** | `CMP bpm, threshold` drives `BGT alert_high` ($Z=0 \land N=V$) | `tests/test_alu.py` |
| `arm_routine.py` | ARM Cortex-M Thumb execution in Unicorn | **Instruction Set Architecture (ISA)** | 4-sample boxcar moving average via `ASRS #2`<br>Instruction-by-instruction register trace ($R0-R7$) | `tests/test_arm_routine.py` |
| `cache.py` | Direct-mapped / Set-associative cache simulator | **Memory Hierarchy & Locality** | 4 KB, 16B lines = 256 lines (4 offset, 8 index, 20 tag bits)<br>$AMAT = t_{\text{hit}} + (M \times t_{\text{miss}})$ | `tests/test_cache.py` |
| `energy.py` | Duty-cycle power model from datasheets | **Low-Power Embedded Architecture** | $I_{\text{avg}} = I_{\text{active}} \cdot D + I_{\text{sleep}} \cdot (1 - D)$<br>8400 $\mu$A active, 1.2 $\mu$A sleep @ 5% = 421.14 $\mu$A (94.99% savings) | `tests/test_energy.py` |
| `pipeline.py` | Integrated physiological signal processing | **System Pipeline Integration** | Classical peak detection (no ML), Q15 boxcar filter, instantaneous BPM | `tests/test_pipeline.py` |
| `run.py` | CLI execution entrypoint | **Command-Line Interface** | `python -m sim.run --config config/default.yaml` | `tests/test_pipeline.py` |

---

## Running Unit Tests
To run tests across all simulation modules:
```bash
pytest tests/ -v
```
To run an individual module test (e.g. Q15):
```bash
pytest tests/test_q15.py -v
```
