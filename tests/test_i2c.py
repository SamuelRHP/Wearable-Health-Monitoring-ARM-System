"""Tests for sim.i2c - I2C Transaction Timing, Protocols, and Bus Utilisation."""

import pytest
from sim.i2c import (
    calculate_sensor_read_cycles,
    calculate_i2c_metrics,
    simulate_i2c_sensor_read,
    I2C_STANDARD_MODE_HZ,
    I2C_FAST_MODE_HZ,
)


def test_i2c_cycle_calculation():
    """Verify cycle count for standard 2-byte sensor register read:

    START (1) + Addr+W (9) + Reg (9) + Sr (1) + Addr+R (9) + MSB (9) + LSB (9) + STOP (1) = 48.
    """
    assert calculate_sensor_read_cycles(data_bytes=2) == 48
    # 1 byte read: 1+9+9+1+9+9+1 = 39 cycles
    assert calculate_sensor_read_cycles(data_bytes=1) == 39


def test_i2c_timing_standard_and_fast_modes():
    """Verify transaction duration at 100 kHz (480 us) and 400 kHz (120 us)."""
    # 100 kHz Standard Mode
    m100 = calculate_i2c_metrics(clock_hz=I2C_STANDARD_MODE_HZ, data_bytes=2, sample_rate_hz=125.0)
    assert m100.total_cycles == 48
    assert pytest.approx(m100.clock_period_us, rel=1e-5) == 10.0
    assert pytest.approx(m100.transaction_duration_us, rel=1e-5) == 480.0
    # Utilisation: 125 * 480 us = 60000 us/s = 6.0%
    assert pytest.approx(m100.bus_utilisation_pct, rel=1e-5) == 6.0

    # 400 kHz Fast Mode
    m400 = calculate_i2c_metrics(clock_hz=I2C_FAST_MODE_HZ, data_bytes=2, sample_rate_hz=125.0)
    assert m400.total_cycles == 48
    assert pytest.approx(m400.clock_period_us, rel=1e-5) == 2.5
    assert pytest.approx(m400.transaction_duration_us, rel=1e-5) == 120.0
    # Utilisation: 125 * 120 us = 15000 us/s = 1.5%
    assert pytest.approx(m400.bus_utilisation_pct, rel=1e-5) == 1.5


def test_simulate_i2c_sensor_read():
    """Verify hardware packet generation from 16-bit sensor reading."""
    pkt = simulate_i2c_sensor_read(
        device_addr_7bit=0x57,
        register_addr=0x07,
        raw_sample_16bit=0x08A0,  # MSB = 0x08 (8), LSB = 0xA0 (160)
    )
    assert pkt.device_address_7bit == 0x57
    assert pkt.register_address == 0x07
    assert pkt.data_bytes == [0x08, 0xA0]
    assert pkt.ack_received is True


def test_i2c_validation_errors():
    """Verify argument bounds checking for physical I2C addresses and clock speeds."""
    with pytest.raises(ValueError, match="device address"):
        simulate_i2c_sensor_read(0x80, 0x00, 0x1234)  # 8-bit address not 7-bit

    with pytest.raises(ValueError, match="register address"):
        simulate_i2c_sensor_read(0x50, 0x100, 0x1234)

    with pytest.raises(ValueError, match="Clock frequency"):
        calculate_i2c_metrics(clock_hz=0)
