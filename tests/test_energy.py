"""Tests for sim.energy - Duty-Cycle Energy Model and Placeholder Verification."""

import pytest
from sim.energy import (
    calculate_energy,
    load_energy_config,
)


def test_energy_worked_example():
    """Verify worked example from the syllabus:

    I_active = 8400 uA, I_sleep = 1.2 uA, active_fraction = 0.05 (5% duty cycle):
    I_avg = (8400 * 0.05) + (1.2 * 0.95) = 420.0 + 1.14 = 421.14 uA.
    saving_pct = (1 - (421.14 / 8400)) * 100% = 94.9864%.
    """
    metrics = calculate_energy(active_fraction=0.05)
    assert pytest.approx(metrics.avg_current_ua, rel=1e-4) == 421.14
    assert pytest.approx(metrics.always_on_ua, rel=1e-4) == 8400.0
    assert pytest.approx(metrics.saving_pct, rel=1e-4) == 94.9864
    assert metrics.placeholder is True
    assert "WARNING" in metrics.warning
    assert "never claim real battery life" in metrics.warning


def test_energy_boundary_cases():
    """Verify energy calculation at extreme duty cycles (100% active, 0% active)."""
    # 100% active (always on): I_avg should equal I_active (saving = 0%)
    m_100 = calculate_energy(active_fraction=1.0)
    assert pytest.approx(m_100.avg_current_ua, rel=1e-4) == 8400.0
    assert pytest.approx(m_100.saving_pct, abs=1e-4) == 0.0

    # 0% active (pure sleep): I_avg should equal I_sleep (saving = 99.9857%)
    m_0 = calculate_energy(active_fraction=0.0)
    assert pytest.approx(m_0.avg_current_ua, rel=1e-4) == 1.2
    assert pytest.approx(m_0.saving_pct, rel=1e-4) == 99.9857


def test_energy_placeholder_flag_and_citation():
    """Verify that source citation contains source name, URL, page, and placeholder status."""
    metrics = calculate_energy()
    assert "STM32L476xx" in metrics.source
    assert "http" in metrics.source
    assert "Page" in metrics.source
    assert metrics.placeholder is True


def test_energy_invalid_duty_cycle():
    """Verify that duty cycle outside [0.0, 1.0] raises ValueError."""
    with pytest.raises(ValueError):
        calculate_energy(active_fraction=-0.1)
    with pytest.raises(ValueError):
        calculate_energy(active_fraction=1.5)
