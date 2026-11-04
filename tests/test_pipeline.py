"""Tests for sim.pipeline - End-to-End Physiological Signal Chain and Subsystem Integration."""

import pytest
from sim.pipeline import (
    generate_synthetic_ppg,
    detect_peaks_classical,
    calculate_bpm_from_peaks,
    run_pipeline,
)


def test_synthetic_ppg_generator():
    """Verify synthetic PPG signal properties: duration, sample count, ADC range [0, 4095]."""
    fs = 125.0
    duration = 5.0
    floats, adcs = generate_synthetic_ppg(duration_s=duration, fs_hz=fs, target_bpm=75.0)

    expected_len = int(fs * duration)
    assert len(floats) == expected_len
    assert len(adcs) == expected_len

    # Assert ADC bounds
    assert min(adcs) >= 0
    assert max(adcs) <= 4095
    # Assert values centered around midscale 2048
    avg_adc = sum(adcs) / len(adcs)
    assert 1800 < avg_adc < 2300


def test_classical_peak_detection():
    """Verify classical peak detection (no ML) identifies cardiac pulses accurately."""
    fs = 125.0
    duration = 10.0
    _, adcs = generate_synthetic_ppg(duration_s=duration, fs_hz=fs, target_bpm=60.0)

    peaks = detect_peaks_classical(adcs, fs_hz=fs)
    # At 60 BPM over 10 seconds, expect approx 9-11 peaks
    assert 8 <= len(peaks) <= 12

    bpm = calculate_bpm_from_peaks(peaks, fs_hz=fs)
    # Estimated BPM should be close to 60 BPM (+- 5 BPM)
    assert 55.0 <= bpm <= 65.0


def test_run_pipeline_normal_rhythm():
    """Verify end-to-end simulation pipeline execution for normal rhythm (no alert)."""
    results = run_pipeline(
        source="synthetic",
        threshold_bpm=120.0,  # High threshold -> normal rhythm, no alert
        duration_s=5.0,
        fs_hz=125.0,
    )

    # 1. Meta
    assert results["meta"]["source"] == "synthetic"
    assert results["meta"]["placeholders_in_use"] is True
    assert len(results["meta"]["warnings"]) > 0

    # 2. Signal
    assert len(results["signal"]["raw_adc"]) == 625
    assert len(results["signal"]["q15"]) == 625
    assert len(results["signal"]["filtered_q15"]) == 625
    assert len(results["signal"]["peaks"]) > 0

    # 3. Heart rate & alert
    assert results["heart_rate"]["bpm"] > 50.0
    assert results["heart_rate"]["alert"] is False

    # 4. Number representation
    last_samp = results["number_repr"]["last_sample"]
    assert "adc" in last_samp and "adc_hex" in last_samp
    assert "q15" in last_samp and "q15_hex" in last_samp
    assert "filtered" in last_samp and "filtered_hex" in last_samp
    assert last_samp["adc_hex"].startswith("0x")

    # 5. ALU
    assert results["alu"]["branch_taken"] is False
    assert set(results["alu"]["flags"].keys()) == {"N", "Z", "C", "V"}

    # 6. Serial
    assert results["serial"]["uart"]["baud"] == 115200
    assert results["serial"]["uart"]["utilisation_pct"] > 0
    assert results["serial"]["i2c"]["clock_hz"] == 100000
    assert results["serial"]["i2c"]["utilisation_pct"] > 0

    # 7. ARM
    assert results["arm"]["matches_python"] is True
    assert len(results["arm"]["steps"]) > 0

    # 8. Cache
    assert results["cache"]["hit_rate"] > 0.8
    assert results["cache"]["amat_cycles"] < results["cache"]["amat_no_cache_cycles"]
    assert results["cache"]["geometry"]["lines"] > 0

    # 9. Energy
    assert results["energy"]["placeholder"] is True
    assert results["energy"]["saving_pct"] > 90.0


def test_run_pipeline_tachycardia_alert():
    """Verify that heart rate above threshold sets ALU flags and triggers alert branch."""
    results = run_pipeline(
        source="synthetic",
        threshold_bpm=50.0,  # Low threshold -> heart rate > threshold triggers alert!
        duration_s=5.0,
        fs_hz=125.0,
    )
    assert results["heart_rate"]["bpm"] > 50.0
    assert results["heart_rate"]["alert"] is True
    assert results["alu"]["branch_taken"] is True


def test_run_pipeline_custom_target_bpm():
    """Verify custom target BPM alters the generated synthetic physiological signal."""
    res_slow = run_pipeline(source="synthetic", target_bpm=55.0, duration_s=10.0)
    res_fast = run_pipeline(source="synthetic", target_bpm=130.0, duration_s=10.0)

    assert len(res_slow["signal"]["peaks"]) < len(res_fast["signal"]["peaks"])
    assert res_slow["heart_rate"]["bpm"] < 70.0
    assert res_fast["heart_rate"]["bpm"] > 115.0
