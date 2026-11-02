"""Wearable Health-Monitoring ARM System - Simulation Core.

This package contains modular, hardware-accurate models of:
- Number representation (sim.q15)
- Serial I/O protocols: UART & I2C (sim.uart, sim.i2c)
- 32-bit Arithmetic Logic Unit with APSR flags (sim.alu)
- ARM Cortex-M Thumb execution via Unicorn (sim.arm_routine)
- Memory hierarchy and Cache simulator (sim.cache)
- Duty-cycle energy model (sim.energy)
- End-to-end signal processing pipeline (sim.pipeline)
"""

__version__ = "1.0.0"
