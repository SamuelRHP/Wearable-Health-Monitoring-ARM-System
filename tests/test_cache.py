"""Tests for sim.cache - Cache Geometry, AMAT, and Hand-Calculated Verification."""

import pytest
from sim.cache import (
    CacheSimulator,
    generate_pipeline_memory_trace,
)


def test_cache_geometry_docstring_example():
    """Verify geometry calculation for syllabus example:

    4 KB Cache, 16-byte line size, Direct-Mapped (associativity = 1).
    Total lines = 4096 / 16 = 256 lines.
    Offset bits = log2(16) = 4 bits (bits [3:0]).
    Index bits = log2(256) = 8 bits (bits [11:4]).
    Tag bits = 32 - 8 - 4 = 20 bits (bits [31:12]).
    """
    sim = CacheSimulator(
        cache_size_bytes=4096,
        line_size_bytes=16,
        associativity=1,
    )
    geom = sim.geometry
    assert geom.lines == 256
    assert geom.offset_bits == 4
    assert geom.index_bits == 8
    assert geom.tag_bits == 20
    assert geom.num_sets == 256


def test_address_decoding():
    """Verify address decoding into tag, index, and offset fields."""
    sim = CacheSimulator(
        cache_size_bytes=4096,
        line_size_bytes=16,
        associativity=1,
    )
    # Address: 0x20000044
    # Binary: 0010 0000 0000 0000 0000 0000 0100 0100
    # Offset (lower 4 bits): 0x4 = 4
    # Index (next 8 bits [11:4]): 0x04 = 4
    # Tag (top 20 bits [31:12]): 0x20000
    tag, index, offset = sim.decode_address(0x20000044)
    assert offset == 4
    assert index == 4
    assert tag == 0x20000


def test_hand_calculated_tiny_trace():
    """Automated Verification Suite: Compare Cache Simulator against Hand-Calculated Reference Trace.

    Configuration:
      Cache Size: 64 bytes
      Line Size: 16 bytes
      Associativity: 1 (Direct-Mapped)
      Number of Sets/Lines: 4 (Index bits = 2, Offset bits = 4, Tag bits = 26)

    Hand Trace:
      1.  0x00: index=0, tag=0 -> MISS (Compulsory). Line 0 now holds tag 0.
      2.  0x04: index=0, tag=0 -> HIT (Spatial locality, line 0 holds 0x00..0x0F).
      3.  0x08: index=0, tag=0 -> HIT.
      4.  0x0C: index=0, tag=0 -> HIT.
      5.  0x10: index=1, tag=0 -> MISS (Compulsory). Line 1 now holds tag 0.
      6.  0x00: index=0, tag=0 -> HIT (Temporal locality).
      7.  0x04: index=0, tag=0 -> HIT.
      8.  0x20: index=2, tag=0 -> MISS (Compulsory). Line 2 now holds tag 0.
      9.  0x10: index=1, tag=0 -> HIT.
      10. 0x00: index=0, tag=0 -> HIT.

    Expected Summary:
      Total Accesses = 10
      Hits = 7
      Misses = 3
      Hit Rate = 7 / 10 = 70.0%
      Miss Rate = 3 / 10 = 30.0%
      AMAT (Hit=1 cycle, Miss=20 cycles) = 1 + (0.30 * 20) = 7.0 cycles.
    """
    cache = CacheSimulator(
        cache_size_bytes=64,
        line_size_bytes=16,
        associativity=1,
        hit_time_cycles=1.0,
        miss_penalty_cycles=20.0,
    )

    trace = [0x00, 0x04, 0x08, 0x0C, 0x10, 0x00, 0x04, 0x20, 0x10, 0x00]
    expected_results = [
        False,  # 0x00 Miss
        True,   # 0x04 Hit
        True,   # 0x08 Hit
        True,   # 0x0C Hit
        False,  # 0x10 Miss
        True,   # 0x00 Hit
        True,   # 0x04 Hit
        False,  # 0x20 Miss
        True,   # 0x10 Hit
        True,   # 0x00 Hit
    ]

    for addr, expected_hit in zip(trace, expected_results):
        actual_hit = cache.access(addr)
        assert actual_hit == expected_hit, f"Address {hex(addr)} expected hit={expected_hit}, got {actual_hit}"

    assert cache.access_count == 10
    assert cache.hit_count == 7
    assert cache.miss_count == 3

    metrics = cache.access_trace([])  # Read out current state
    assert metrics.hit_rate == 0.7
    assert metrics.miss_rate == 0.3
    assert metrics.amat_cycles == 7.0
    assert metrics.amat_no_cache_cycles == 20.0


def test_set_associative_lru_replacement():
    """Verify 2-Way Set-Associative Cache with LRU replacement."""
    # 32 bytes cache, 8-byte lines, 2-way associative -> 2 sets
    # Set index = bit [3], Offset = bits [2:0], Tag = bits [31:4]
    cache = CacheSimulator(
        cache_size_bytes=32,
        line_size_bytes=8,
        associativity=2,
    )

    # 1. Access 0x00 (Set 0, Tag 0) -> Miss, stored in way 0
    assert cache.access(0x00) is False
    # 2. Access 0x10 (Set 0, Tag 1) -> Miss, stored in way 1 (no eviction needed, 2-way)
    assert cache.access(0x10) is False
    # 3. Access 0x00 again -> Hit (way 0 still present!)
    assert cache.access(0x00) is True
    # 4. Access 0x20 (Set 0, Tag 2) -> Miss, must evict LRU line (way 1 was last accessed before way 0)
    assert cache.access(0x20) is False
    # 5. Access 0x00 -> Hit!
    assert cache.access(0x00) is True
    # 6. Access 0x10 -> Miss (was evicted by 0x20)
    assert cache.access(0x10) is False


def test_pipeline_trace_locality():
    """Verify high hit rate on the physiological signal processing pipeline memory trace."""
    cache = CacheSimulator(
        cache_size_bytes=1024,
        line_size_bytes=16,
        associativity=1,
    )
    trace = generate_pipeline_memory_trace(num_samples=100)
    metrics = cache.access_trace(trace)

    # Signal processing circular buffer accesses exhibit heavy spatial and temporal locality
    assert metrics.hit_rate > 0.85
    assert metrics.amat_cycles < metrics.amat_no_cache_cycles
