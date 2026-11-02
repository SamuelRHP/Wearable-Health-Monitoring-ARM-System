# Automated Test Suite (`tests/`)

This directory contains the unit tests and verification suites for all modules in the project.

## Test Structure
Every simulation core module has a corresponding test file:

| Test File | Target Module | What It Tests | COA Concept Demonstrated |
| :--- | :--- | :--- | :--- |
| `test_q15.py` | `sim/q15.py` | Q15 float conversions, saturation, two's complement, saturating add, multiply with shift, 12-bit ADC quantization, error bounds. | **Number Representation & Fixed-Point** |
| `test_uart.py` | `sim/uart.py` | 8-N-1 UART framing, start/stop bits, framing errors, baud timing, and bus utilisation (115200 baud). | **Asynchronous Serial I/O** |
| `test_i2c.py` | `sim/i2c.py` | I2C transaction cycle counts (48 cycles for 2 bytes), 100 kHz / 400 kHz durations, bus utilisation. | **Synchronous Serial Interconnect** |
| `test_alu.py` | `sim/alu.py` | 32-bit `ADD`, `SUB`, `CMP`, `ASR`, `LSL`, `LSR`, truth tables for $N, Z, C, V$ flags, and `BGT` alert branching. | **ALU Architecture & Flags** |
| `test_arm_routine.py` | `sim/arm_routine.py` | Thumb instruction execution in Unicorn emulator, register tracing ($R0-R7$), and 500-vector bit-exact match with Python. | **ARM ISA & Microarchitecture** |
| `test_cache.py` | `sim/cache.py` | 32-bit address decoding, geometry, 10-address hand-calculated trace verification, LRU replacement, and AMAT. | **Cache Hierarchy & Locality** |
| `test_energy.py` | `sim/energy.py` | Duty-cycle equation, extreme active fractions, YAML configuration loading, and placeholder warning verification. | **Low-Power Architecture** |
| `test_pipeline.py` | `sim/pipeline.py` | Integrated signal acquisition, peak detection (no ML), BPM calculation, and full pipeline flow. | **Hardware Signal Path Integration** |
| `test_api.py` | `backend/api.py` | FastAPI endpoints (`/api/health`, `/api/defaults`, `/api/records`, `/api/run`, `/api/verification`) and 422 validation. | **System API & Interface** |

---

## Running Tests
Run the entire suite:
```bash
pytest -v
```

Run a specific test file:
```bash
pytest tests/test_cache.py -v
```

Generate test coverage report:
```bash
pytest --cov=sim --cov=backend
```
