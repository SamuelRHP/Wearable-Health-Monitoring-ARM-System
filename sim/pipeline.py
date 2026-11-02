"""End-to-end Wearable Health-Monitoring ARM Simulation Pipeline.

COA Integrated Pipeline
-----------------------
This module integrates all Computer Organization and Architecture blocks:
1. Signal Acquisition: PhysioNet BIDMC PPG record or deterministic synthetic generator.
2. Number Representation: 12-bit unsigned ADC -> signed 16-bit Q15 fixed-point.
3. ARM Cortex-M Filtering: 4-sample moving average filter boxcar executed in Unicorn.
4. Classical Signal Processing: Peak detection and heart rate (BPM) extraction (NO ML).
5. 32-bit ALU Decision: CMP heart_rate, threshold driving conditional branch BGT.
6. Serial Interconnect: UART telemetry framing and I2C sensor bus timing & utilisation.
7. Cache Simulation: Execution trace through configurable cache, computing AMAT.
8. Duty-Cycle Energy Model: Average current, baseline, and power savings from datasheets.
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import Sequence, Any, Tuple

from sim.q15 import (
    to_q15,
    from_q15,
    adc_to_q15,
    to_hex_12,
    to_hex_16,
    Q15_MIN,
    Q15_MAX,
    ADC_12BIT_MIDSCALE,
)
from sim.alu import ALU, evaluate_condition
from sim.uart import calculate_uart_metrics
from sim.i2c import calculate_i2c_metrics
from sim.cache import CacheSimulator, generate_pipeline_memory_trace
from sim.arm_routine import execute_moving_average_unicorn, moving_average_4_python
from sim.energy import calculate_energy


def generate_synthetic_ppg(
    duration_s: float = 10.0,
    fs_hz: float = 125.0,
    target_bpm: float = 75.0,
    noise_amplitude: float = 0.02,
) -> tuple[list[float], list[int]]:
    """Generate a realistic, deterministic PPG pulse waveform for offline simulation.

    Anatomy of Synthetic PPG:
    - Systolic peak (cardiac pulse fundamental at target_bpm / 60)
    - Dicrotic notch and diastolic wave (second harmonic shifted in phase)
    - Respiratory baseline wander (0.25 Hz slow modulation)
    - High-frequency sensor noise

    Returns:
        (float_signal_normalized, adc_12bit_integers)
    """
    num_samples = int(duration_s * fs_hz)
    f0 = target_bpm / 60.0  # Pulse frequency in Hz
    f_resp = 0.25           # Respiration frequency in Hz (15 breaths/min)

    float_signal: list[float] = []
    adc_signal: list[int] = []

    for i in range(num_samples):
        t = i / fs_hz

        # Cardiac pulse with systolic peak and dicrotic notch
        phase = 2.0 * math.pi * f0 * t
        systolic = 0.65 * math.sin(phase)
        dicrotic = 0.25 * math.sin(2.0 * phase - 1.2)
        harm3 = 0.10 * math.sin(3.0 * phase - 2.0)
        pulse = systolic + dicrotic + harm3

        # Respiration baseline wander
        baseline = 0.12 * math.sin(2.0 * math.pi * f_resp * t)

        # Deterministic pseudo-random sensor noise
        noise = noise_amplitude * math.sin(53.0 * t) * math.cos(31.0 * t)

        # Combined signal normalized approximately in [-0.8, 0.8]
        norm_val = 0.75 * pulse + baseline + noise

        # Clamp to [-0.95, 0.95]
        norm_val = max(-0.95, min(0.95, norm_val))
        float_signal.append(norm_val)

        # Convert to 12-bit unsigned ADC integer [0, 4095] with midscale at 2048
        adc_int = int(round(norm_val * 2000.0)) + ADC_12BIT_MIDSCALE
        adc_int = max(0, min(4095, adc_int))
        adc_signal.append(adc_int)

    return float_signal, adc_signal


def load_physionet_record(
    record_name: str = "bidmc01",
    duration_s: float = 10.0,
    fs_hz: float = 125.0,
) -> tuple[list[float], list[int], list[str]]:
    """Load a real PPG recording from PhysioNet BIDMC repository using wfdb.

    If network or local file is unavailable, automatically falls back to synthetic generator.

    Returns:
        (float_signal, adc_samples, warnings)
    """
    warnings: list[str] = []
    data_dir = Path(__file__).resolve().parent.parent / "data"

    try:
        import wfdb
        # Attempt loading from local data/ directory first
        record = None
        local_path = data_dir / record_name
        if (local_path.with_suffix(".hea")).exists():
            record = wfdb.rdrecord(str(local_path))
        else:
            # Attempt streaming from PhysioNet BIDMC repository
            record = wfdb.rdrecord(record_name, pn_dir="bidmc/1.0.0")

        if record is not None and "PLETH" in record.sig_name:
            channel_idx = record.sig_name.index("PLETH")
            raw_floats = record.p_signal[:, channel_idx]
            native_fs = float(record.fs)

            # Slice duration
            num_samples = int(duration_s * native_fs)
            sliced = raw_floats[:num_samples]

            # Normalize to 12-bit ADC [0, 4095]
            min_v = float(min(sliced))
            max_v = float(max(sliced))
            rng = max_v - min_v if max_v > min_v else 1.0

            adc_samples = [
                int(round(((v - min_v) / rng) * 4095.0))
                for v in sliced
            ]
            normalized_floats = [
                ((adc - ADC_12BIT_MIDSCALE) / 2048.0)
                for adc in adc_samples
            ]
            return normalized_floats, adc_samples, warnings
        else:
            warnings.append(f"Channel PLETH not found in PhysioNet record {record_name}; used synthetic fallback.")
    except Exception as exc:
        warnings.append(
            f"PhysioNet fetch for {record_name} failed ({exc}); used offline synthetic fallback."
        )

    # Fallback generator
    floats, adcs = generate_synthetic_ppg(duration_s=duration_s, fs_hz=fs_hz)
    return floats, adcs, warnings


def detect_peaks_classical(
    signal: Sequence[int],
    fs_hz: float = 125.0,
    min_distance_s: float = 0.35,  # Max heart rate ~170 bpm
) -> list[int]:
    """Detect pulse peaks using classical signal processing (moving threshold + refractory period).

    HARD CONSTRAINT: Strictly NO machine learning.
    Uses local peak detection with refractory spacing.
    """
    if len(signal) < 5:
        return []

    min_samples_distance = int(min_distance_s * fs_hz)
    peaks: list[int] = []

    # Dynamic threshold: 60th percentile / mean + 0.3 * std
    mean_val = sum(signal) / len(signal)
    variance = sum((x - mean_val) ** 2 for x in signal) / len(signal)
    std_val = math.sqrt(variance)
    threshold = mean_val + (0.25 * std_val)

    last_peak = -min_samples_distance

    for i in range(1, len(signal) - 1):
        # Local maximum above threshold
        if signal[i] > signal[i - 1] and signal[i] >= signal[i + 1]:
            if signal[i] > threshold and (i - last_peak) >= min_samples_distance:
                peaks.append(i)
                last_peak = i

    return peaks


def calculate_bpm_from_peaks(
    peaks: Sequence[int],
    fs_hz: float = 125.0,
    default_bpm: float = 75.0,
) -> float:
    """Compute instantaneous/average heart rate in Beats Per Minute (BPM) from peak intervals."""
    if len(peaks) < 2:
        return default_bpm

    intervals_sec = [
        (peaks[i] - peaks[i - 1]) / fs_hz
        for i in range(1, len(peaks))
    ]
    mean_rr_sec = sum(intervals_sec) / len(intervals_sec)
    if mean_rr_sec <= 0:
        return default_bpm

    bpm = 60.0 / mean_rr_sec
    return round(bpm, 2)


def run_pipeline(
    source: str = "synthetic",
    threshold_bpm: float = 100.0,
    cache_size_bytes: int = 4096,
    line_size_bytes: int = 16,
    associativity: int = 1,
    active_fraction: float = 0.05,
    duration_s: float = 10.0,
    fs_hz: float = 125.0,
) -> dict[str, Any]:
    """Execute the full integrated COA simulation pipeline.

    Returns:
        JSON-compliant dictionary matching the REST API schema.
    """
    warnings: list[str] = []

    # 1. Acquire raw physiological signal
    if source.lower() == "synthetic":
        norm_floats, raw_adcs = generate_synthetic_ppg(
            duration_s=duration_s,
            fs_hz=fs_hz,
            target_bpm=75.0,
        )
    else:
        norm_floats, raw_adcs, fetch_warnings = load_physionet_record(
            record_name=source,
            duration_s=duration_s,
            fs_hz=fs_hz,
        )
        warnings.extend(fetch_warnings)

    # 2. Number Representation: 12-bit ADC to Q15
    q15_signal = [adc_to_q15(adc) for adc in raw_adcs]

    # 3. ARM Cortex-M 4-Sample Moving Average Filter
    filtered_q15: list[int] = []
    for i in range(len(q15_signal)):
        if i < 3:
            filtered_q15.append(q15_signal[i])
        else:
            # 4-sample window: [sample[i-3], sample[i-2], sample[i-1], sample[i]]
            window = [
                q15_signal[i - 3],
                q15_signal[i - 2],
                q15_signal[i - 1],
                q15_signal[i],
            ]
            avg, _ = moving_average_4_python(window, threshold=0)
            filtered_q15.append(avg)

    # 4. Classical Peak Detection & BPM Calculation
    peaks = detect_peaks_classical(filtered_q15, fs_hz=fs_hz)
    calculated_bpm = calculate_bpm_from_peaks(peaks, fs_hz=fs_hz)

    # 5. 32-bit ALU Decision Logic (CMP bpm, threshold)
    bpm_int = int(round(calculated_bpm))
    thresh_int = int(round(threshold_bpm))
    alu_sub = ALU.sub(bpm_int, thresh_int)
    branch_taken = evaluate_condition("GT", alu_sub.flags)
    alert_active = branch_taken

    # 6. Serial Interconnect Modeling
    uart_metrics = calculate_uart_metrics(
        baud_rate=115200,
        packet_bytes=8,
        packet_rate_hz=fs_hz,
    )
    i2c_metrics = calculate_i2c_metrics(
        clock_hz=100000,
        data_bytes=2,
        sample_rate_hz=fs_hz,
    )

    # 7. ARM Execution Trace (Representative 4-sample window in Unicorn)
    rep_window = q15_signal[:4] if len(q15_signal) >= 4 else [1000, 2000, 3000, 4000]
    arm_unicorn_res = execute_moving_average_unicorn(
        samples=rep_window,
        threshold=int(round(threshold_bpm * 100)),  # Scaled threshold
        trace_steps=True,
    )

    # 8. Cache Memory Simulator & AMAT
    cache_sim = CacheSimulator(
        cache_size_bytes=cache_size_bytes,
        line_size_bytes=line_size_bytes,
        associativity=associativity,
        hit_time_cycles=1.0,
        miss_penalty_cycles=20.0,
    )
    trace = generate_pipeline_memory_trace(num_samples=len(q15_signal))
    cache_metrics = cache_sim.access_trace(trace)

    # 9. Duty-Cycle Energy Model
    energy_metrics = calculate_energy(active_fraction=active_fraction)
    if energy_metrics.placeholder:
        warnings.append(energy_metrics.warning)

    # 10. Assemble Number Representation for last sample
    last_adc = raw_adcs[-1] if raw_adcs else 0
    last_q15 = q15_signal[-1] if q15_signal else 0
    last_filtered = filtered_q15[-1] if filtered_q15 else 0

    number_repr_payload = {
        "last_sample": {
            "adc": last_adc,
            "adc_hex": to_hex_12(last_adc),
            "q15": last_q15,
            "q15_hex": to_hex_16(last_q15),
            "filtered": last_filtered,
            "filtered_hex": to_hex_16(last_filtered),
        }
    }

    # Format final payload strictly matching contract
    return {
        "meta": {
            "source": source,
            "fs_hz": fs_hz,
            "duration_s": duration_s,
            "placeholders_in_use": energy_metrics.placeholder,
            "warnings": warnings,
        },
        "signal": {
            "raw_adc": raw_adcs,
            "q15": q15_signal,
            "filtered_q15": filtered_q15,
            "peaks": peaks,
        },
        "heart_rate": {
            "bpm": calculated_bpm,
            "alert": alert_active,
        },
        "number_repr": number_repr_payload,
        "alu": {
            "result": alu_sub.result,
            "flags": alu_sub.flags.to_dict(),
            "branch_taken": branch_taken,
        },
        "serial": {
            "uart": {
                "baud": uart_metrics.baud_rate,
                "bytes_per_s": uart_metrics.throughput_bytes_per_s,
                "packet_bytes": uart_metrics.packet_bytes,
                "utilisation_pct": round(uart_metrics.bus_utilisation_pct, 4),
            },
            "i2c": {
                "clock_hz": i2c_metrics.clock_hz,
                "transaction_us": round(i2c_metrics.transaction_duration_us, 2),
                "utilisation_pct": round(i2c_metrics.bus_utilisation_pct, 4),
            },
        },
        "arm": {
            "steps": arm_unicorn_res["steps"],
            "matches_python": arm_unicorn_res["matches_python"],
        },
        "cache": {
            "hit_rate": cache_metrics.hit_rate,
            "miss_rate": cache_metrics.miss_rate,
            "amat_cycles": cache_metrics.amat_cycles,
            "amat_no_cache_cycles": cache_metrics.amat_no_cache_cycles,
            "geometry": cache_metrics.geometry.to_dict(),
        },
        "energy": {
            "avg_current_ua": energy_metrics.avg_current_ua,
            "always_on_ua": energy_metrics.always_on_ua,
            "saving_pct": energy_metrics.saving_pct,
            "placeholder": energy_metrics.placeholder,
            "source": energy_metrics.source,
        },
    }
