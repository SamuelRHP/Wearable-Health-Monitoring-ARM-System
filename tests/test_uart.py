"""Tests for sim.uart - UART Framing, Timing, and Bus Utilisation."""

import pytest
from sim.uart import (
    encode_uart_byte,
    decode_uart_byte,
    encode_uart_packet,
    decode_uart_packet,
    calculate_uart_metrics,
    FramingError,
)


def test_uart_byte_encoding_and_framing():
    """Verify 10-bit 8-N-1 frame construction: Start=0, 8 data bits LSB-first, Stop=1."""
    # 0x41 = 65 = 0b01000001 (LSB is 1, MSB is 0)
    frame = encode_uart_byte(0x41)
    assert len(frame) == 10
    assert frame[0] == 0   # Start bit
    assert frame[1] == 1   # D0 (LSB)
    assert frame[2] == 0   # D1
    assert frame[3] == 0   # D2
    assert frame[4] == 0   # D3
    assert frame[5] == 0   # D4
    assert frame[6] == 0   # D5
    assert frame[7] == 1   # D6
    assert frame[8] == 0   # D7 (MSB)
    assert frame[9] == 1   # Stop bit

    # Decode round-trip
    assert decode_uart_byte(frame) == 0x41


def test_uart_round_trip_all_byte_patterns():
    """Verify round-trip encoding and decoding across key bit patterns."""
    test_bytes = [0x00, 0xFF, 0x55, 0xAA, 0x01, 0x80, 0x7F]
    for b in test_bytes:
        frame = encode_uart_byte(b)
        assert decode_uart_byte(frame) == b


def test_uart_framing_errors():
    """Verify FramingError triggers on invalid start or stop bits."""
    valid_frame = encode_uart_byte(0x55)

    # Corrupt start bit (set to 1 instead of 0)
    bad_start = list(valid_frame)
    bad_start[0] = 1
    with pytest.raises(FramingError, match="Start bit"):
        decode_uart_byte(bad_start)

    # Corrupt stop bit (set to 0 instead of 1)
    bad_stop = list(valid_frame)
    bad_stop[9] = 0
    with pytest.raises(FramingError, match="Stop bit"):
        decode_uart_byte(bad_stop)

    # Invalid frame length
    with pytest.raises(FramingError, match="10-bit"):
        decode_uart_byte(valid_frame[:9])


def test_uart_packet_stream():
    """Verify multi-byte telemetry packet serialization."""
    payload = b"HR:075BPM"
    bitstream = encode_uart_packet(payload)
    assert len(bitstream) == len(payload) * 10
    decoded = decode_uart_packet(bitstream)
    assert decoded == payload


def test_uart_metrics_worked_example():
    """Verify the worked example from the syllabus:

    115200 baud, 10 bits per byte = 11520 bytes/s.
    An 8-byte packet at 100 Hz needs 800 B/s.
    Utilisation = 800 / 11520 * 100% = 6.9444%.
    """
    metrics = calculate_uart_metrics(
        baud_rate=115200,
        packet_bytes=8,
        packet_rate_hz=100.0,
        bits_per_frame=10,
    )
    assert metrics.max_bytes_per_s == 11520.0
    assert metrics.throughput_bytes_per_s == 800.0
    assert pytest.approx(metrics.bus_utilisation_pct, rel=1e-4) == 6.9444
    assert pytest.approx(metrics.byte_duration_us, rel=1e-4) == 86.8055
