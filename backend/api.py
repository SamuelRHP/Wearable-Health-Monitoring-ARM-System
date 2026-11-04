"""FastAPI Backend Application for Wearable Health-Monitoring ARM System.

COA Backend Service
-------------------
Provides a RESTful API interfacing the Python simulation core:
- CORS middleware enabled for localhost origins.
- Serves static assets from frontend/ when directory exists.
- GET /api/health: Heartbeat status.
- GET /api/defaults: Simulation configuration, ranges, and placeholder alerts.
- GET /api/records: List of verified PhysioNet BIDMC records and synthetic source.
- POST /api/run: Validates parameters, executes simulation, returns full COA subsystem metrics.
- GET /api/verification: Automated verification tests for Q15, ARM Unicorn, and Cache.
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import Any, List, Optional
import yaml

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from sim.pipeline import run_pipeline, generate_synthetic_ppg
from sim.q15 import to_q15, compute_quantization_error
from sim.arm_routine import execute_moving_average_unicorn
from sim.cache import CacheSimulator
from sim.energy import load_energy_config


# Initialize FastAPI application
app = FastAPI(
    title="Wearable Health-Monitoring ARM System API",
    description="Backend API simulating an energy-conscious ARM Cortex-M processor for continuous physiological monitoring.",
    version="1.0.0",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# Custom plain-language 422 error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format Pydantic validation errors into plain-language messages."""
    error_messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Invalid parameter")
        error_messages.append(f"Parameter '{field}': {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": error_messages},
    )


# Request Body Model for POST /api/run
class RunSimulationRequest(BaseModel):
    source: str = Field(
        default="synthetic",
        description="Signal source ('synthetic', 'bidmc01', 'bidmc02')",
    )
    threshold_bpm: float = Field(
        default=100.0,
        description="Heart rate alert threshold in beats per minute (40.0 to 220.0)",
    )
    cache_size_bytes: int = Field(
        default=4096,
        description="Cache capacity in bytes (must be power of 2, 64 to 65536)",
    )
    line_size_bytes: int = Field(
        default=16,
        description="Cache line size in bytes (must be power of 2, 4 to 128)",
    )
    associativity: int = Field(
        default=1,
        description="Cache associativity (1 = direct-mapped, 2, 4, 8, 16-way)",
    )
    active_fraction: float = Field(
        default=0.05,
        description="Duty-cycle active fraction (0.001 to 1.0)",
    )
    duration_s: float = Field(
        default=10.0,
        description="Window duration in seconds (1.0 to 60.0)",
    )
    target_bpm: float = Field(
        default=75.0,
        description="Simulated target heart rate in beats per minute for synthetic generator (40.0 to 220.0)",
    )

    @field_validator("target_bpm")
    @classmethod
    def validate_target_bpm(cls, v: float) -> float:
        if v < 40.0 or v > 220.0:
            raise ValueError("Target BPM must be between 40.0 and 220.0 BPM (physiological limits)")
        return v

    @field_validator("threshold_bpm")
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        if v < 40.0 or v > 220.0:
            raise ValueError("Threshold must be between 40.0 and 220.0 BPM (physiological limits)")
        return v

    @field_validator("duration_s")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        if v < 1.0 or v > 60.0:
            raise ValueError("Duration must be between 1.0 and 60.0 seconds")
        return v

    @field_validator("active_fraction")
    @classmethod
    def validate_active_fraction(cls, v: float) -> float:
        if v < 0.001 or v > 1.0:
            raise ValueError("Active fraction must be between 0.001 (0.1%) and 1.0 (100%)")
        return v

    @field_validator("cache_size_bytes")
    @classmethod
    def validate_cache_size(cls, v: int) -> int:
        if v < 64 or v > 65536:
            raise ValueError("Cache size must be between 64 bytes and 65,536 bytes (64 KB)")
        if (v & (v - 1)) != 0:
            raise ValueError("Cache size must be a power of 2 (e.g., 512, 1024, 2048, 4096)")
        return v

    @field_validator("line_size_bytes")
    @classmethod
    def validate_line_size(cls, v: int) -> int:
        if v < 4 or v > 128:
            raise ValueError("Line size must be between 4 bytes and 128 bytes")
        if (v & (v - 1)) != 0:
            raise ValueError("Line size must be a power of 2 (e.g., 8, 16, 32, 64)")
        return v

    @field_validator("associativity")
    @classmethod
    def validate_associativity(cls, v: int) -> int:
        if v not in (1, 2, 4, 8, 16):
            raise ValueError("Associativity must be one of [1, 2, 4, 8, 16]")
        return v


@app.get("/api/health")
def get_health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/defaults")
def get_defaults() -> dict[str, Any]:
    """Return default simulation parameters, valid validation ranges, and placeholder status."""
    default_cfg_path = CONFIG_DIR / "default.yaml"
    with open(default_cfg_path, "r", encoding="utf-8") as f:
        default_data = yaml.safe_load(f)

    energy_data = load_energy_config()

    return {
        "defaults": {
            "source": default_data["simulation"]["source"],
            "threshold_bpm": default_data["simulation"]["threshold_bpm"],
            "target_bpm": default_data["simulation"].get("target_bpm", 75.0),
            "cache_size_bytes": default_data["cache"]["cache_size_bytes"],
            "line_size_bytes": default_data["cache"]["line_size_bytes"],
            "associativity": default_data["cache"]["associativity"],
            "active_fraction": default_data["energy"]["active_fraction"],
            "duration_s": default_data["simulation"]["duration_s"],
            "fs_hz": default_data["simulation"]["fs_hz"],
        },
        "validation_ranges": default_data["validation_ranges"],
        "placeholders": {
            "energy_parameters": energy_data.get("is_placeholder", True),
            "warning": energy_data.get("placeholder_warning", ""),
            "target_mcu": energy_data.get("target_mcu", ""),
            "source": energy_data.get("source", {}),
        },
    }


@app.get("/api/records")
def get_records() -> list[str]:
    """Return available verified PhysioNet records and the synthetic generator."""
    return ["bidmc01", "bidmc02", "synthetic"]


@app.post("/api/run")
def post_run(req: RunSimulationRequest) -> dict[str, Any]:
    """Execute the simulation pipeline with validated parameters and return COA subsystem metrics."""
    try:
        results = run_pipeline(
            source=req.source,
            threshold_bpm=req.threshold_bpm,
            cache_size_bytes=req.cache_size_bytes,
            line_size_bytes=req.line_size_bytes,
            associativity=req.associativity,
            active_fraction=req.active_fraction,
            duration_s=req.duration_s,
            target_bpm=req.target_bpm,
        )
        return results
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation execution failed: {str(exc)}",
        )


@app.get("/api/verification")
def get_verification() -> dict[str, Any]:
    """Run automated verification checks:

    1. Q15 versus IEEE 754 Float precision error on PPG signal.
    2. Emulated ARM Thumb routine (Unicorn) versus pure Python reference.
    3. Cache simulator versus hand-calculated reference trace.
    """
    # 1. Q15 vs Float check
    float_samples, _ = generate_synthetic_ppg(duration_s=2.0, fs_hz=125.0)
    q15_samples = [to_q15(f) for f in float_samples]
    q15_err = compute_quantization_error(float_samples, q15_samples)
    q15_passed = q15_err["max_absolute_error"] < 5e-4

    # 2. Emulated ARM vs Python check (100 random trials)
    import random
    random.seed(1337)
    arm_passed = True
    mismatches = 0
    for _ in range(100):
        test_samples = [random.randint(-30000, 30000) for _ in range(4)]
        thresh = random.randint(-20000, 20000)
        res = execute_moving_average_unicorn(test_samples, thresh, trace_steps=False)
        if not res["matches_python"]:
            arm_passed = False
            mismatches += 1

    # 3. Cache simulator vs hand calculation
    cache = CacheSimulator(
        cache_size_bytes=64,
        line_size_bytes=16,
        associativity=1,
        hit_time_cycles=1.0,
        miss_penalty_cycles=20.0,
    )
    hand_trace = [0x00, 0x04, 0x08, 0x0C, 0x10, 0x00, 0x04, 0x20, 0x10, 0x00]
    expected_hits = [False, True, True, True, False, True, True, False, True, True]
    actual_hits = [cache.access(addr) for addr in hand_trace]
    cache_passed = (actual_hits == expected_hits) and (cache.hit_count == 7) and (cache.miss_count == 3)

    all_passed = q15_passed and arm_passed and cache_passed

    return {
        "all_passed": all_passed,
        "checks": {
            "q15_vs_float": {
                "name": "Q15 vs Float Reference",
                "passed": q15_passed,
                "max_absolute_error": q15_err["max_absolute_error"],
                "mean_absolute_error": q15_err["mean_absolute_error"],
                "rmse": q15_err["rmse"],
                "snr_db": round(q15_err["snr_db"], 2),
            },
            "arm_vs_python": {
                "name": "Emulated ARM vs Pure Python",
                "passed": arm_passed,
                "vectors_tested": 100,
                "matches_python": arm_passed,
                "mismatches": mismatches,
            },
            "cache_vs_hand_calc": {
                "name": "Cache Simulator vs Hand Calculation",
                "passed": cache_passed,
                "total_accesses": 10,
                "expected_hits": 7,
                "actual_hits": cache.hit_count,
                "hit_rate": cache.hit_count / 10.0,
                "amat_cycles": 1.0 + ((cache.miss_count / 10.0) * 20.0),
            },
        },
    }


DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def _parse_markdown_table(file_path: Path) -> list[dict[str, str]]:
    """Parse a Markdown table into a list of row dictionaries."""
    if not file_path.exists():
        return []
    lines = [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("|")
    ]
    if len(lines) < 3:
        return []
    headers = [h.strip() for h in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        row = {}
        for h, c in zip(headers, cells):
            clean_c = c.replace("`[PASTE FROM SYLLABUS]`", "To be confirmed from the syllabus")
            clean_c = clean_c.replace("[PASTE FROM SYLLABUS]", "To be confirmed from the syllabus")
            clean_c = clean_c.replace("**", "")
            row[h] = clean_c
        rows.append(row)
    return rows


@app.get("/api/traceability")
def get_traceability() -> dict[str, Any]:
    """Return course outcomes and dimension mapping parsed from docs/CO_MAPPING.md and docs/DIMENSION.md."""
    co_rows = _parse_markdown_table(DOCS_DIR / "CO_MAPPING.md")
    dim_rows = _parse_markdown_table(DOCS_DIR / "DIMENSION.md")
    return {
        "course_outcomes": co_rows,
        "dimensions": dim_rows,
        "co_file": "docs/CO_MAPPING.md",
        "dim_file": "docs/DIMENSION.md",
    }


# Mount frontend static directory if present
if FRONTEND_DIR.exists() and any(FRONTEND_DIR.iterdir()):
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

