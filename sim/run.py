"""Command-Line Interface (CLI) runner for the Wearable Health-Monitoring ARM System.

Usage:
    python -m sim.run --config config/default.yaml
    python -m sim.run --source bidmc01 --threshold 100 --duration 10.0
"""

from __future__ import annotations
import argparse
import csv
from pathlib import Path
import sys
import yaml

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt

from sim.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Wearable Health-Monitoring ARM Architecture Simulation."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/default.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Signal source: 'synthetic', 'bidmc01', 'bidmc02'",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Heart rate alert threshold in BPM",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Signal duration in seconds",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory for generated plots, CSV and Markdown reports",
    )
    return parser.parse_args()


def save_csv_results(data: dict, output_file: Path) -> None:
    """Save time-series data of ADC, Q15, and filtered samples to CSV."""
    raw_adc = data["signal"]["raw_adc"]
    q15 = data["signal"]["q15"]
    filtered_q15 = data["signal"]["filtered_q15"]
    peaks_set = set(data["signal"]["peaks"])
    fs_hz = data["meta"]["fs_hz"]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_index", "time_s", "raw_adc", "q15", "filtered_q15", "is_peak"])
        for i in range(len(raw_adc)):
            t = round(i / fs_hz, 4)
            is_peak = 1 if i in peaks_set else 0
            writer.writerow([i, t, raw_adc[i], q15[i], filtered_q15[i], is_peak])


def save_plot_results(data: dict, output_file: Path) -> None:
    """Generate and save publication-grade plot of the physiological signal chain."""
    raw_adc = data["signal"]["raw_adc"]
    q15 = data["signal"]["q15"]
    filtered_q15 = data["signal"]["filtered_q15"]
    peaks = data["signal"]["peaks"]
    fs_hz = data["meta"]["fs_hz"]
    time_axis = [i / fs_hz for i in range(len(raw_adc))]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    fig.suptitle(
        f"Wearable Health-Monitoring ARM System - Physiological Signal Processing\n"
        f"Source: {data['meta']['source']} | Heart Rate: {data['heart_rate']['bpm']} BPM | "
        f"Alert: {data['heart_rate']['alert']}",
        fontsize=12,
        fontweight="bold",
    )

    # Top Plot: Raw 12-bit ADC Signal and Detected Peaks
    ax1.plot(time_axis, raw_adc, label="12-bit ADC (Raw PPG)", color="#1f77b4", linewidth=1.2)
    if peaks:
        peak_times = [p / fs_hz for p in peaks]
        peak_values = [raw_adc[p] for p in peaks]
        ax1.scatter(peak_times, peak_values, color="red", s=40, zorder=5, label="Systolic Peaks (BPM)")
    ax1.set_ylabel("ADC Code [0, 4095]")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="upper right")

    # Bottom Plot: Q15 Fixed-Point vs ARM Filtered Output
    ax2.plot(time_axis, q15, label="Signed Q15 (Raw)", color="#aec7e8", alpha=0.7, linewidth=1.0)
    ax2.plot(time_axis, filtered_q15, label="4-Sample Moving Avg (ARM Thumb)", color="#2ca02c", linewidth=1.5)
    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("Q15 Integer [-32768, 32767]")
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="upper right")

    plt.tight_layout()
    fig.savefig(output_file, dpi=200)
    plt.close(fig)


def save_markdown_summary(data: dict, output_file: Path) -> None:
    """Generate Markdown summary table covering all integrated COA concepts."""
    meta = data["meta"]
    hr = data["heart_rate"]
    num = data["number_repr"]["last_sample"]
    alu = data["alu"]
    flags = alu["flags"]
    serial = data["serial"]
    cache = data["cache"]
    energy = data["energy"]

    content = f"""# Wearable Health-Monitoring ARM System - Simulation Summary

**Student:** Samuel Rohlupuia  
**Course Outcomes Covered:** CO1 to CO6 (Architecture, ALU, Serial I/O, Cache, Power Optimization)  
**Signal Source:** `{meta['source']}` | **Duration:** {meta['duration_s']} s | **Sampling Frequency:** {meta['fs_hz']} Hz  

---

## 1. Physiological Monitoring & Alert Decision
| Metric | Value | COA Relevance |
| :--- | :--- | :--- |
| **Instantaneous Heart Rate** | **{hr['bpm']} BPM** | Classical peak detection (refractory spacing, no ML) |
| **Alert Status** | **{'ACTIVE (ALERT TRIGGERED)' if hr['alert'] else 'NORMAL (MONITORING)'}** | Driven by ARM CMP bpm, threshold and conditional branch (BGT) |
| **ALU Subtraction Result** | `{alu['result']}` | $BPM - \\text{{threshold}}$ |
| **APSR Status Flags** | `N={flags['N']}, Z={flags['Z']}, C={flags['C']}, V={flags['V']}` | Condition evaluation: $Z=0 \\land N=V$ |
| **Branch Taken** | `{alu['branch_taken']}` | Microarchitectural program flow diversion |

---

## 2. Number Representation & Hardware Quantization (Last Sample)
| Stage | Integer Value | Hexadecimal Format | COA Concept |
| :--- | :--- | :--- | :--- |
| **Raw 12-bit ADC** | `{num['adc']}` | `{num['adc_hex']}` | Unsigned integer digitization [0, 4095] |
| **Signed Q15 Fixed-Point** | `{num['q15']}` | `{num['q15_hex']}` | Hardware bit-shift: `(ADC - 2048) << 4` |
| **ARM Filtered Output** | `{num['filtered']}` | `{num['filtered_hex']}` | 4-sample boxcar FIR filter (`ASRS #2`) |

---

## 3. Serial Interconnect Bandwidth & Utilisation
| Protocol | Channel Parameter | Transaction / Frame Latency | Bus Utilisation (%) | COA Concept |
| :--- | :--- | :--- | :--- | :--- |
| **UART Telemetry** | {serial['uart']['baud']} baud (8-N-1) | 8-byte packet @ {meta['fs_hz']} Hz | **{serial['uart']['utilisation_pct']}%** | Asynchronous serial framing & bandwidth |
| **I2C Sensor Bus** | {serial['i2c']['clock_hz'] // 1000} kHz | {serial['i2c']['transaction_us']} $\\mu$s per reading | **{serial['i2c']['utilisation_pct']}%** | Synchronous 2-wire bus timing & overhead |

---

## 4. Cache Memory Hierarchy & AMAT
| Parameter | Value | Architectural Interpretation |
| :--- | :--- | :--- |
| **Cache Geometry** | {cache['geometry']['lines']} lines ({cache['geometry']['offset_bits']} offset bits, {cache['geometry']['index_bits']} index bits, {cache['geometry']['tag_bits']} tag bits) | 32-bit address decomposition |
| **Hit Rate** | **{round(cache['hit_rate'] * 100, 2)}%** | Spatial and temporal locality over circular buffer |
| **Miss Rate** | **{round(cache['miss_rate'] * 100, 2)}%** | Cold misses and capacity replacements |
| **AMAT with Cache** | **{cache['amat_cycles']} cycles** | $t_{{hit}} + (\\text{{Miss Rate}} \\times t_{{miss}})$ |
| **AMAT without Cache** | **{cache['amat_no_cache_cycles']} cycles** | Off-chip Flash / SRAM latency penalty |
| **Effective Speedup** | **{round(cache['amat_no_cache_cycles'] / cache['amat_cycles'], 2)}x** | Performance benefit of caching |

---

## 5. Duty-Cycle Energy Model
| Metric | Value | Datasheet Context |
| :--- | :--- | :--- |
| **Average Current Draw** | **{energy['avg_current_ua']} $\\mu$A** | $I_{{avg}} = I_{{active}} \\cdot D + I_{{sleep}} \\cdot (1 - D)$ |
| **Always-On Baseline** | **{energy['always_on_ua']} $\\mu$A** | Unoptimized continuous full-speed clocking |
| **Estimated Energy Savings** | **{energy['saving_pct']}%** | Battery life extension via sleep modes |
| **Datasheet Source** | `{energy['source']}` | Manufacturer figures |

> [!WARNING]
> **Hard Constraint Notice:** Energy metrics are **estimated from datasheet figures** (marked PLACEHOLDER). Never claim real battery life.

---

## 6. Active System Warnings
"""
    if meta["warnings"]:
        for w in meta["warnings"]:
            content += f"- {w}\n"
    else:
        content += "- None. All subsystems executed within nominal operational bounds.\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    args = parse_args()

    # Load configuration file
    config_path = Path(args.config)
    config: dict = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    sim_cfg = config.get("simulation", {})
    cache_cfg = config.get("cache", {})
    energy_cfg = config.get("energy", {})

    source = args.source or sim_cfg.get("source", "synthetic")
    threshold_bpm = args.threshold if args.threshold is not None else float(sim_cfg.get("threshold_bpm", 100.0))
    duration_s = args.duration if args.duration is not None else float(sim_cfg.get("duration_s", 10.0))
    fs_hz = float(sim_cfg.get("fs_hz", 125.0))

    cache_size = int(cache_cfg.get("cache_size_bytes", 4096))
    line_size = int(cache_cfg.get("line_size_bytes", 16))
    assoc = int(cache_cfg.get("associativity", 1))
    active_frac = float(energy_cfg.get("active_fraction", 0.05))

    print("================================================================================")
    print("      Wearable Health-Monitoring ARM System - Simulation Core Runner           ")
    print("================================================================================")
    print(f"Configuration:   {config_path}")
    print(f"Signal Source:   {source} (Duration: {duration_s}s, Fs: {fs_hz}Hz)")
    print(f"Threshold:       {threshold_bpm} BPM | Active Fraction: {active_frac * 100}%")
    print(f"Cache Geometry:  {cache_size}B ({line_size}B lines, {assoc}-way)")
    print("--------------------------------------------------------------------------------")

    # Run simulation pipeline
    results = run_pipeline(
        source=source,
        threshold_bpm=threshold_bpm,
        cache_size_bytes=cache_size,
        line_size_bytes=line_size,
        associativity=assoc,
        active_fraction=active_frac,
        duration_s=duration_s,
        fs_hz=fs_hz,
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_file = out_dir / "simulation_results.csv"
    plot_file = out_dir / "ppg_pipeline_plot.png"
    summary_file = out_dir / "simulation_summary.md"

    save_csv_results(results, csv_file)
    save_plot_results(results, plot_file)
    save_markdown_summary(results, summary_file)

    hr = results["heart_rate"]
    cache = results["cache"]
    energy = results["energy"]

    print(f"\n[+] Results generated in '{out_dir.resolve()}':")
    print(f"    - Plot:    {plot_file.name}")
    print(f"    - CSV:     {csv_file.name}")
    print(f"    - Summary: {summary_file.name}")
    print("\n--- Key Performance Indicators ---")
    print(f"Heart Rate:       {hr['bpm']} BPM (Alert: {'ACTIVE' if hr['alert'] else 'NORMAL'})")
    print(f"Cache Hit Rate:   {round(cache['hit_rate'] * 100, 2)}% (AMAT: {cache['amat_cycles']} cycles)")
    print(f"Energy Savings:   {energy['saving_pct']}% (Avg Current: {energy['avg_current_ua']} uA)")
    print(f"ARM Verification: {'100% Bit-Exact Match with Python' if results['arm']['matches_python'] else 'MISMATCH'}")

    if results["meta"]["warnings"]:
        print("\n[!] Warnings in effect:")
        for w in results["meta"]["warnings"]:
            print(f"    {w}")

    print("================================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
