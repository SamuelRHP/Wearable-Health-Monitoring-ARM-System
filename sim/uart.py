"""UART (Universal Asynchronous Receiver-Transmitter) protocol and bus utilization model.

COA Concept: Asynchronous Serial Communication & Bus Bandwidth
--------------------------------------------------------------
Wearable devices transmit physiological metrics (e.g., heart rate, alert flags, raw PPG)
to host applications or Bluetooth Low Energy (BLE) companion modules over a serial UART link.
UART is asynchronous: sender and receiver agree beforehand on the baud rate (bits per second)
and bit framing, eliminating the need for a shared clock wire.

Framing Format (Standard 8-N-1):
-------------------------------
Every transmitted byte is wrapped in a 10-bit hardware frame:
1. Start Bit: 1 bit at logic LOW (0), signalling the receiver to synchronize its internal baud timer.
2. Data Bits: 8 bits sent Least Significant Bit (LSB) first.
3. Parity Bit: None in 8-N-1 (0 bits).
4. Stop Bit: 1 bit at logic HIGH (1), returning the line to idle.
Total physical bits per byte = 1 + 8 + 0 + 1 = 10 bits.

Worked Examples for Students:
-----------------------------
1. Maximum Throughput Calculation:
   At 115,200 baud with 10 bits per frame:
   max_bytes_per_s = 115200 / 10 = 11,520 bytes/s.
2. Bus Utilisation of Health Telemetry:
   Suppose an 8-byte health alert packet is transmitted at 100 Hz (100 times per second):
   required_throughput = 8 bytes * 100 Hz = 800 bytes/s.
   bus_utilisation = (800 bytes/s / 11520 bytes/s) * 100% = 6.9444%.
3. Bit-level frame serialization:
   Byte 0x41 ('A' = 0b01000001, LSB=1, MSB=0):
   Frame: [Start=0, D0=1, D1=0, D2=0, D3=0, D4=0, D5=0, D6=1, D7=0, Stop=1].
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence


class FramingError(ValueError):
    """Raised when a received bitstream violates UART framing rules (missing start or stop bit)."""
    pass


@dataclass(frozen=True)
class UARTMetrics:
    """Calculated metrics for a UART transmission scenario."""
    baud_rate: int
    bits_per_frame: int
    max_bytes_per_s: float
    byte_duration_us: float
    packet_bytes: int
    packet_rate_hz: float
    throughput_bytes_per_s: float
    bus_utilisation_pct: float


def encode_uart_byte(byte_val: int) -> list[int]:
    """Encode an 8-bit integer [0, 255] into a standard 10-bit 8-N-1 UART frame.

    Bits are ordered: [Start Bit (0), Data LSB -> MSB, Stop Bit (1)].

    Worked Example:
        >>> encode_uart_byte(0x41)  # 0x41 = 65 = 0b01000001
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 1]
    """
    if byte_val < 0 or byte_val > 255:
        raise ValueError(f"Byte value {byte_val} outside 8-bit range [0, 255]")

    # Start bit is active LOW (0)
    frame = [0]
    # 8 data bits, LSB first
    for i in range(8):
        frame.append((byte_val >> i) & 1)
    # Stop bit is active HIGH (1)
    frame.append(1)
    return frame


def decode_uart_byte(frame: Sequence[int]) -> int:
    """Decode a 10-bit 8-N-1 UART frame into an 8-bit integer.

    COA Concept: Framing Error Detection.
    Verifies that bit 0 is logic LOW (0) and bit 9 is logic HIGH (1).
    Raises FramingError if framing rules are violated.

    Worked Example:
        >>> decode_uart_byte([0, 1, 0, 0, 0, 0, 0, 1, 0, 1])
        65
    """
    if len(frame) != 10:
        raise FramingError(f"Expected 10-bit frame, got {len(frame)} bits")
    if frame[0] != 0:
        raise FramingError(f"Framing error: Start bit must be 0, got {frame[0]}")
    if frame[9] != 1:
        raise FramingError(f"Framing error: Stop bit must be 1, got {frame[9]}")

    byte_val = 0
    for i in range(8):
        bit = frame[1 + i]
        if bit not in (0, 1):
            raise FramingError(f"Invalid logic level {bit} at data bit {i}")
        byte_val |= (bit << i)
    return byte_val


def encode_uart_packet(data: bytes) -> list[int]:
    """Encode a multi-byte payload into a contiguous stream of UART frames."""
    bitstream: list[int] = []
    for b in data:
        bitstream.extend(encode_uart_byte(b))
    return bitstream


def decode_uart_packet(bitstream: Sequence[int]) -> bytes:
    """Decode a contiguous stream of 10-bit UART frames into bytes."""
    if len(bitstream) % 10 != 0:
        raise FramingError(
            f"Bitstream length ({len(bitstream)}) is not a multiple of 10-bit frames"
        )
    output = bytearray()
    for i in range(0, len(bitstream), 10):
        frame = bitstream[i : i + 10]
        output.append(decode_uart_byte(frame))
    return bytes(output)


def calculate_uart_metrics(
    baud_rate: int = 115200,
    packet_bytes: int = 8,
    packet_rate_hz: float = 100.0,
    bits_per_frame: int = 10,
) -> UARTMetrics:
    """Calculate transmission timing, bandwidth, and bus utilisation for a UART channel.

    COA Concept: Serial Bus Bandwidth & Utilisation Analysis.

    Worked Example:
        At 115200 baud, 8-byte packet at 100 Hz:
        >>> m = calculate_uart_metrics(115200, 8, 100.0)
        >>> round(m.max_bytes_per_s, 2)
        11520.0
        >>> round(m.bus_utilisation_pct, 4)
        6.9444
    """
    if baud_rate <= 0:
        raise ValueError("Baud rate must be positive")
    if packet_bytes < 0:
        raise ValueError("Packet bytes cannot be negative")
    if packet_rate_hz < 0:
        raise ValueError("Packet rate cannot be negative")

    max_bytes_per_s = baud_rate / bits_per_frame
    byte_duration_us = (bits_per_frame / baud_rate) * 1_000_000.0
    throughput_bytes_per_s = packet_bytes * packet_rate_hz
    bus_utilisation_pct = (
        (throughput_bytes_per_s / max_bytes_per_s) * 100.0
        if max_bytes_per_s > 0
        else 0.0
    )

    return UARTMetrics(
        baud_rate=baud_rate,
        bits_per_frame=bits_per_frame,
        max_bytes_per_s=max_bytes_per_s,
        byte_duration_us=byte_duration_us,
        packet_bytes=packet_bytes,
        packet_rate_hz=packet_rate_hz,
        throughput_bytes_per_s=throughput_bytes_per_s,
        bus_utilisation_pct=bus_utilisation_pct,
    )
