"""I2C (Inter-Integrated Circuit) transaction protocol and bus utilization model.

COA Concept: Synchronous Serial Bus & Protocol Timing
-----------------------------------------------------
Wearable health systems acquire physiological readings from digital sensors
(e.g., PPG pulse oximeters, skin temperature sensors, 3-axis accelerometers)
over an I2C bus. Unlike asynchronous UART, I2C is synchronous: it shares a
Serial Clock Line (SCL) driven by the microcontroller (bus master) and a
bidirectional Serial Data Line (SDA).

I2C Transaction Anatomy:
------------------------
A standard register read transaction consists of:
1. START Condition (S): SDA pulled LOW while SCL is HIGH (1 clock equivalent).
2. Device Address (7 bits) + Write bit (0) + Slave ACK (1 bit) = 9 clock cycles.
3. Register Pointer (8 bits) + Slave ACK (1 bit) = 9 clock cycles.
4. REPEATED START Condition (Sr): 1 clock cycle.
5. Device Address (7 bits) + Read bit (1) + Slave ACK (1 bit) = 9 clock cycles.
6. Data Bytes: Each received byte takes 8 data bits + 1 Master ACK/NACK bit = 9 clock cycles.
7. STOP Condition (P): SDA released HIGH while SCL is HIGH (1 clock equivalent).

Total Clock Cycles for 2-byte Sensor Read (e.g., 12-bit ADC sample):
Cycles = 1 (START) + 9 (Addr+W) + 9 (Reg) + 1 (Sr) + 9 (Addr+R) + 9 (Data MSB) + 9 (Data LSB) + 1 (STOP)
       = 48 clock cycles.

Worked Examples for Students:
-----------------------------
1. Transaction Duration at Standard Mode (100 kHz):
   Clock frequency = 100,000 Hz -> Clock period T = 10.0 microseconds.
   Duration = 48 cycles * 10.0 us = 480.0 microseconds.
2. Transaction Duration at Fast Mode (400 kHz):
   Clock frequency = 400,000 Hz -> Clock period T = 2.5 microseconds.
   Duration = 48 cycles * 2.5 us = 120.0 microseconds.
3. Bus Utilisation at 125 Hz PPG Sampling Rate:
   125 sensor readings per second at 100 kHz:
   Active bus time per second = 125 * 480 us = 60,000 us = 0.060 seconds.
   Bus utilisation = (0.060 s / 1.0 s) * 100% = 6.0%.
   At 400 kHz:
   Active bus time = 125 * 120 us = 15,000 us = 0.015 seconds -> 1.5% utilisation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Literal


I2C_STANDARD_MODE_HZ: int = 100_000   # 100 kHz
I2C_FAST_MODE_HZ: int = 400_000       # 400 kHz


@dataclass(frozen=True)
class I2CTransactionMetrics:
    """Calculated metrics for an I2C sensor read transaction."""
    clock_hz: int
    clock_period_us: float
    total_cycles: int
    transaction_duration_us: float
    sample_rate_hz: float
    bus_utilisation_pct: float
    data_bytes: int


@dataclass
class I2CPacket:
    """Represents a validated I2C transaction sequence."""
    device_address_7bit: int
    register_address: int
    data_bytes: list[int]
    is_read: bool = True
    ack_received: bool = True


def calculate_sensor_read_cycles(data_bytes: int = 2) -> int:
    """Calculate the total clock cycles required for an I2C combined write-pointer + read transaction.

    COA Concept: Hardware Protocol Overhead.
    Anatomy:
      START (1) + Addr+W (9) + Reg (9) + Sr (1) + Addr+R (9) + [Data (9) * data_bytes] + STOP (1)
    """
    if data_bytes <= 0:
        raise ValueError("Data bytes must be at least 1")
    return 1 + 9 + 9 + 1 + 9 + (9 * data_bytes) + 1


def calculate_i2c_metrics(
    clock_hz: int = I2C_STANDARD_MODE_HZ,
    data_bytes: int = 2,
    sample_rate_hz: float = 125.0,
) -> I2CTransactionMetrics:
    """Calculate the timing, duration, and bus utilisation for an I2C sensor reading.

    COA Concept: Synchronous Serial Bus Timing & Capacity Planning.

    Worked Example:
        >>> m100 = calculate_i2c_metrics(100_000, 2, 125.0)
        >>> m100.transaction_duration_us
        480.0
        >>> m100.bus_utilisation_pct
        6.0
        >>> m400 = calculate_i2c_metrics(400_000, 2, 125.0)
        >>> m400.transaction_duration_us
        120.0
        >>> m400.bus_utilisation_pct
        1.5
    """
    if clock_hz <= 0:
        raise ValueError("Clock frequency must be positive")
    if sample_rate_hz < 0:
        raise ValueError("Sample rate cannot be negative")

    clock_period_us = (1.0 / clock_hz) * 1_000_000.0
    total_cycles = calculate_sensor_read_cycles(data_bytes)
    transaction_duration_us = total_cycles * clock_period_us
    bus_active_time_us = transaction_duration_us * sample_rate_hz
    bus_utilisation_pct = (bus_active_time_us / 1_000_000.0) * 100.0

    return I2CTransactionMetrics(
        clock_hz=clock_hz,
        clock_period_us=clock_period_us,
        total_cycles=total_cycles,
        transaction_duration_us=transaction_duration_us,
        sample_rate_hz=sample_rate_hz,
        bus_utilisation_pct=bus_utilisation_pct,
        data_bytes=data_bytes,
    )


def simulate_i2c_sensor_read(
    device_addr_7bit: int,
    register_addr: int,
    raw_sample_16bit: int,
) -> I2CPacket:
    """Simulate the physical I2C transaction transferring a 16-bit sensor reading (MSB, LSB).

    Worked Example:
        >>> pkt = simulate_i2c_sensor_read(0x57, 0x07, 0x08A0)
        >>> pkt.data_bytes
        [8, 160]
    """
    if device_addr_7bit < 0 or device_addr_7bit > 0x7F:
        raise ValueError(f"Invalid 7-bit device address: {hex(device_addr_7bit)}")
    if register_addr < 0 or register_addr > 0xFF:
        raise ValueError(f"Invalid 8-bit register address: {hex(register_addr)}")

    msb = (raw_sample_16bit >> 8) & 0xFF
    lsb = raw_sample_16bit & 0xFF

    return I2CPacket(
        device_address_7bit=device_addr_7bit,
        register_address=register_addr,
        data_bytes=[msb, lsb],
        is_read=True,
        ack_received=True,
    )
