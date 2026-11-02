"""Configurable direct-mapped and set-associative cache simulator.

COA Concept: Memory Hierarchy, Locality of Reference, and AMAT
--------------------------------------------------------------
Microcontrollers executing continuous physiological algorithms (such as filtering
and peak detection) perform frequent memory accesses to circular sample buffers
and filter coefficient tables. Caches exploit two fundamental properties:
1. Temporal Locality: If a memory location is accessed, it is likely to be accessed again soon.
2. Spatial Locality: If a memory location is accessed, nearby memory locations are likely
   to be accessed soon.

Address Partitioning (32-bit Memory Address):
--------------------------------------------
A 32-bit memory address is partitioned into three fields:
    [        Tag Bits (t)        |   Index Bits (s)   |   Offset Bits (b)   ]
- Offset bits (b): log2(line_size_bytes) -> Identifies byte within a cache line.
- Index bits (s): log2(num_sets) -> Selects the cache set.
- Tag bits (t): 32 - s - b -> Validates whether the cached line matches the request.

Worked Examples for Students:
-----------------------------
1. Geometry Calculation (Direct-Mapped Cache):
   Parameters: Cache size = 4 KB (4096 bytes), Line size = 16 bytes, Associativity = 1.
   Number of lines / sets = 4096 / 16 = 256 lines.
   Offset bits: b = log2(16) = 4 bits (bits [3:0]).
   Index bits:  s = log2(256) = 8 bits (bits [11:4]).
   Tag bits:    t = 32 - 8 - 4 = 20 bits (bits [31:12]).

2. Average Memory Access Time (AMAT):
   AMAT models the effective memory access latency of the system:
       AMAT = Hit_Time + (Miss_Rate * Miss_Penalty)
   Suppose Hit_Time = 1 cycle (SRAM cache), Miss_Penalty = 20 cycles (Flash memory),
   and the cache achieves a 95% Hit Rate (Miss Rate = 5% = 0.05):
       AMAT = 1 + (0.05 * 20) = 1 + 1.0 = 2.0 cycles.
   Without a cache, every single memory access suffers the full miss penalty:
       AMAT_no_cache = 20.0 cycles.
   Speedup from cache = 20.0 / 2.0 = 10x!
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Sequence, List, Dict, Any


@dataclass(frozen=True)
class CacheGeometry:
    """Structural breakdown of cache address fields."""
    cache_size_bytes: int
    line_size_bytes: int
    associativity: int
    num_sets: int
    offset_bits: int
    index_bits: int
    tag_bits: int

    @property
    def lines(self) -> int:
        return self.num_sets * self.associativity

    def to_dict(self) -> dict[str, int]:
        return {
            "lines": self.lines,
            "offset_bits": self.offset_bits,
            "index_bits": self.index_bits,
            "tag_bits": self.tag_bits,
        }


@dataclass(frozen=True)
class CacheMetrics:
    """Performance evaluation metrics for a simulation run."""
    total_accesses: int
    hits: int
    misses: int
    hit_rate: float
    miss_rate: float
    amat_cycles: float
    amat_no_cache_cycles: float
    geometry: CacheGeometry

    def to_dict(self) -> dict[str, Any]:
        return {
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
            "amat_cycles": self.amat_cycles,
            "amat_no_cache_cycles": self.amat_no_cache_cycles,
            "geometry": self.geometry.to_dict(),
        }


@dataclass
class CacheLine:
    """Represents a single cache line (block)."""
    valid: bool = False
    tag: int = 0
    last_access_time: int = 0


class CacheSimulator:
    """Configurable Direct-Mapped and N-Way Set-Associative Cache Simulator with LRU replacement."""

    def __init__(
        self,
        cache_size_bytes: int = 4096,
        line_size_bytes: int = 16,
        associativity: int = 1,
        hit_time_cycles: float = 1.0,
        miss_penalty_cycles: float = 20.0,
    ) -> None:
        if cache_size_bytes <= 0 or (cache_size_bytes & (cache_size_bytes - 1)) != 0:
            raise ValueError(f"Cache size ({cache_size_bytes}) must be a positive power of 2")
        if line_size_bytes <= 0 or (line_size_bytes & (line_size_bytes - 1)) != 0:
            raise ValueError(f"Line size ({line_size_bytes}) must be a positive power of 2")
        if associativity <= 0 or (associativity & (associativity - 1)) != 0:
            raise ValueError(f"Associativity ({associativity}) must be a positive power of 2")

        total_lines = cache_size_bytes // line_size_bytes
        if total_lines < associativity:
            raise ValueError(
                f"Cache size ({cache_size_bytes}B) cannot accommodate {associativity}-way "
                f"associativity with line size {line_size_bytes}B"
            )

        self.cache_size_bytes = cache_size_bytes
        self.line_size_bytes = line_size_bytes
        self.associativity = associativity
        self.hit_time_cycles = hit_time_cycles
        self.miss_penalty_cycles = miss_penalty_cycles

        self.num_sets = total_lines // associativity
        self.offset_bits = int(math.log2(line_size_bytes))
        self.index_bits = int(math.log2(self.num_sets))
        self.tag_bits = 32 - self.offset_bits - self.index_bits

        self.geometry = CacheGeometry(
            cache_size_bytes=self.cache_size_bytes,
            line_size_bytes=self.line_size_bytes,
            associativity=self.associativity,
            num_sets=self.num_sets,
            offset_bits=self.offset_bits,
            index_bits=self.index_bits,
            tag_bits=self.tag_bits,
        )

        # Initialize sets: list of sets, each set is a list of CacheLine objects
        self.sets: List[List[CacheLine]] = [
            [CacheLine() for _ in range(self.associativity)] for _ in range(self.num_sets)
        ]

        # Performance counters
        self.access_count: int = 0
        self.hit_count: int = 0
        self.miss_count: int = 0
        self.current_time: int = 0

    def decode_address(self, address: int) -> tuple[int, int, int]:
        """Decode a 32-bit address into (tag, index, offset).

        Worked Example:
            >>> cache = CacheSimulator(cache_size_bytes=4096, line_size_bytes=16, associativity=1)
            >>> tag, index, offset = cache.decode_address(0x20000044)
            >>> offset
            4
        """
        addr_32 = address & 0xFFFFFFFF
        offset_mask = (1 << self.offset_bits) - 1
        offset = addr_32 & offset_mask

        index_mask = (1 << self.index_bits) - 1
        index = (addr_32 >> self.offset_bits) & index_mask

        tag = addr_32 >> (self.offset_bits + self.index_bits)
        return tag, index, offset

    def access(self, address: int) -> bool:
        """Simulate a memory access to the specified 32-bit address.

        Returns:
            True if Hit, False if Miss.
        """
        self.access_count += 1
        self.current_time += 1
        tag, index, offset = self.decode_address(address)
        cache_set = self.sets[index]

        # 1. Search for a matching valid tag in the set (Hit)
        for line in cache_set:
            if line.valid and line.tag == tag:
                line.last_access_time = self.current_time
                self.hit_count += 1
                return True

        # 2. Cache Miss: find an invalid line or evict LRU line
        self.miss_count += 1
        lru_index = 0
        min_access_time = float("inf")

        # Find first invalid line, or the one with the smallest last_access_time
        for i, line in enumerate(cache_set):
            if not line.valid:
                lru_index = i
                break
            if line.last_access_time < min_access_time:
                min_access_time = line.last_access_time
                lru_index = i

        # Replace / populate line
        cache_set[lru_index].valid = True
        cache_set[lru_index].tag = tag
        cache_set[lru_index].last_access_time = self.current_time
        return False

    def access_trace(self, addresses: Sequence[int]) -> CacheMetrics:
        """Run a sequential sequence of memory addresses through the cache and return metrics."""
        for addr in addresses:
            self.access(addr)

        hit_rate = round(self.hit_count / self.access_count, 6) if self.access_count > 0 else 0.0
        miss_rate = round(1.0 - hit_rate, 6)
        amat = round(self.hit_time_cycles + (miss_rate * self.miss_penalty_cycles), 6)
        amat_no_cache = round(self.miss_penalty_cycles, 6)

        return CacheMetrics(
            total_accesses=self.access_count,
            hits=self.hit_count,
            misses=self.miss_count,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            amat_cycles=amat,
            amat_no_cache_cycles=amat_no_cache,
            geometry=self.geometry,
        )

    def reset(self) -> None:
        """Reset all cache lines and counters."""
        for s in self.sets:
            for line in s:
                line.valid = False
                line.tag = 0
                line.last_access_time = 0
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
        self.current_time = 0


def generate_pipeline_memory_trace(
    num_samples: int,
    base_sram_addr: int = 0x20000000,
    circular_buffer_len: int = 16,
) -> list[int]:
    """Generate the memory address trace produced by the wearable filtering pipeline.

    COA Concept: Spatial and Temporal Locality in Signal Processing Pipelines.
    For each incoming 16-bit Q15 sample:
    1. Write new sample to circular buffer: 1 write (2 bytes).
    2. Read last 4 samples for moving average: 4 reads (2 bytes each).
    3. Write filtered sample to output history buffer: 1 write.
    """
    trace: list[int] = []
    output_base_addr = base_sram_addr + (circular_buffer_len * 2)

    for i in range(num_samples):
        # Index in circular buffer
        buf_idx = i % circular_buffer_len
        sample_addr = base_sram_addr + (buf_idx * 2)

        # 1. Write new sample
        trace.append(sample_addr)

        # 2. Read 4 samples for moving average filter
        for tap in range(4):
            read_idx = (buf_idx - tap) % circular_buffer_len
            trace.append(base_sram_addr + (read_idx * 2))

        # 3. Write filtered output
        out_addr = output_base_addr + ((i % circular_buffer_len) * 2)
        trace.append(out_addr)

    return trace
