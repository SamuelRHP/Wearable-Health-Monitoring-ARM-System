"""Duty-cycle energy and power consumption model for ARM Cortex-M wearables.

COA Concept: Power-Aware Architecture, Sleep Modes & Duty-Cycling
------------------------------------------------------------------
In battery-powered wearable physiological monitors, energy is the primary design
constraint. Rather than operating continuously at full clock frequency, modern
low-power processors (such as the ARM Cortex-M4/M33 with ARM TrustZone and
autonomous sleep controllers) operate in a duty-cycled regime:
1. Active State (Run Mode): The CPU wakes up on timer/DMA interrupt, acquires a batch
   of sensor samples, filters them, computes heart rate, and executes alert logic.
2. Sleep State (Stop / Standby Mode): The core gates CPU clocks (WFI - Wait For Interrupt)
   and shuts down high-speed oscillators, dropping current consumption by over 3 orders
   of magnitude while retaining SRAM state and real-time counter (RTC).

Mathematical Duty-Cycle Model:
------------------------------
Average current draw over time is modeled as:
    I_avg = (I_active * D) + (I_sleep * (1 - D))
where D is the active duty-cycle fraction:
    D = T_active / (T_active + T_sleep)
Energy savings compared to an un-optimized always-on architecture:
    Saving (%) = (1 - (I_avg / I_active)) * 100%

Worked Example for Students:
-----------------------------
Using datasheet figures for STM32L476RG (marked PLACEHOLDER):
- Run Mode (active at 80 MHz, 3.0V): I_active = 8400 uA (8.4 mA).
- Stop 2 Mode (sleep with RTC, 3.0V): I_sleep = 1.2 uA.
- Active fraction D = 0.05 (5% active duty cycle):
  I_avg = (8400 * 0.05) + (1.2 * 0.95)
        = 420.0 uA + 1.14 uA = 421.14 uA.
  Baseline always-on current = 8400 uA.
  Saving (%) = (1 - (421.14 / 8400)) * 100% = 94.9864%.
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import yaml


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "energy_params.yaml"


@dataclass(frozen=True)
class EnergyMetrics:
    """Estimated energy consumption and duty cycle savings."""
    avg_current_ua: float
    always_on_ua: float
    saving_pct: float
    placeholder: bool
    source: str
    warning: str

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary conforming to REST API schema."""
        return {
            "avg_current_ua": self.avg_current_ua,
            "always_on_ua": self.always_on_ua,
            "saving_pct": self.saving_pct,
            "placeholder": self.placeholder,
            "source": self.source,
        }


def load_energy_config(config_path: Path | str | None = None) -> dict[str, Any]:
    """Load energy parameters and placeholder metadata from YAML configuration."""
    target_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"Energy configuration file not found at {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def calculate_energy(
    active_fraction: float | None = None,
    config_path: Path | str | None = None,
) -> EnergyMetrics:
    """Calculate average current consumption, always-on baseline, and power savings.

    COA Concept: Duty-Cycle Power Modeling & Datasheet Energy Estimation.
    All results are explicitly labeled as estimated from datasheet figures.
    """
    config = load_energy_config(config_path)
    is_placeholder = bool(config.get("is_placeholder", True))
    warning = str(config.get("placeholder_warning", "WARNING: Energy parameters are unverified PLACEHOLDER values."))

    source_info = config.get("source", {})
    source_name = source_info.get("name", "Datasheet PLACEHOLDER")
    source_url = source_info.get("url", "")
    source_page = source_info.get("page", "")
    full_source = f"{source_name} (Page {source_page}, {source_url})"

    params = config.get("parameters", {})
    i_active_ua = float(params.get("active_current_ua", 8400.0))
    i_sleep_ua = float(params.get("sleep_current_ua", 1.2))

    if active_fraction is None:
        duty_cycle = float(params.get("default_active_fraction", 0.05))
    else:
        duty_cycle = float(active_fraction)

    if duty_cycle < 0.0 or duty_cycle > 1.0:
        raise ValueError(f"Active fraction {duty_cycle} must be in range [0.0, 1.0]")

    avg_current_ua = (i_active_ua * duty_cycle) + (i_sleep_ua * (1.0 - duty_cycle))
    always_on_ua = i_active_ua

    saving_pct = ((1.0 - (avg_current_ua / always_on_ua)) * 100.0) if always_on_ua > 0 else 0.0

    return EnergyMetrics(
        avg_current_ua=round(avg_current_ua, 4),
        always_on_ua=round(always_on_ua, 4),
        saving_pct=round(saving_pct, 4),
        placeholder=is_placeholder,
        source=full_source,
        warning=warning,
    )
