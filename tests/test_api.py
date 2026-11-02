"""Tests for backend.api - FastAPI Endpoints, Validation, and REST Contract."""

import pytest
from fastapi.testclient import TestClient
from backend.api import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_api_health(client):
    """Verify GET /api/health returns status ok."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_api_defaults(client):
    """Verify GET /api/defaults returns parameters, validation ranges, and placeholder info."""
    resp = client.get("/api/defaults")
    assert resp.status_code == 200
    data = resp.json()
    assert "defaults" in data
    assert "validation_ranges" in data
    assert "placeholders" in data
    assert data["placeholders"]["energy_parameters"] is True


def test_api_records(client):
    """Verify GET /api/records returns list of available sources."""
    resp = client.get("/api/records")
    assert resp.status_code == 200
    records = resp.json()
    assert "synthetic" in records
    assert "bidmc01" in records


def test_api_run_valid_synthetic(client):
    """Verify POST /api/run returns 200 and matches the exact specified schema."""
    payload = {
        "source": "synthetic",
        "threshold_bpm": 100.0,
        "cache_size_bytes": 4096,
        "line_size_bytes": 16,
        "associativity": 1,
        "active_fraction": 0.05,
        "duration_s": 5.0,
    }
    resp = client.post("/api/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Exact top-level field names assertion
    required_keys = {
        "meta",
        "signal",
        "heart_rate",
        "number_repr",
        "alu",
        "serial",
        "arm",
        "cache",
        "energy",
    }
    assert required_keys.issubset(data.keys())

    # Check signal fields
    assert "raw_adc" in data["signal"]
    assert "q15" in data["signal"]
    assert "filtered_q15" in data["signal"]
    assert "peaks" in data["signal"]

    # Check number_repr fields
    num = data["number_repr"]["last_sample"]
    assert set(num.keys()) == {"adc", "adc_hex", "q15", "q15_hex", "filtered", "filtered_hex"}

    # Check alu fields
    assert "result" in data["alu"]
    assert "branch_taken" in data["alu"]
    assert set(data["alu"]["flags"].keys()) == {"N", "Z", "C", "V"}

    # Check serial fields
    assert set(data["serial"]["uart"].keys()) == {"baud", "bytes_per_s", "packet_bytes", "utilisation_pct"}
    assert set(data["serial"]["i2c"].keys()) == {"clock_hz", "transaction_us", "utilisation_pct"}

    # Check arm fields
    assert "steps" in data["arm"]
    assert data["arm"]["matches_python"] is True

    # Check cache fields
    assert set(data["cache"].keys()) == {"hit_rate", "miss_rate", "amat_cycles", "amat_no_cache_cycles", "geometry"}
    assert set(data["cache"]["geometry"].keys()) == {"lines", "offset_bits", "index_bits", "tag_bits"}

    # Check energy fields
    assert set(data["energy"].keys()) == {"avg_current_ua", "always_on_ua", "saving_pct", "placeholder", "source"}
    assert data["energy"]["placeholder"] is True


def test_api_run_validation_errors(client):
    """Verify POST /api/run returns 422 with plain-language error message for invalid inputs."""
    # Threshold out of range (< 40 BPM)
    bad_thresh = {"threshold_bpm": 20.0}
    resp = client.post("/api/run", json=bad_thresh)
    assert resp.status_code == 422
    err_text = str(resp.json())
    assert "Threshold must be between 40.0 and 220.0 BPM" in err_text

    # Cache size not power of 2
    bad_cache = {"cache_size_bytes": 500}
    resp = client.post("/api/run", json=bad_cache)
    assert resp.status_code == 422
    assert "Cache size must be a power of 2" in str(resp.json())

    # Duration out of range (> 60 s)
    bad_dur = {"duration_s": 120.0}
    resp = client.post("/api/run", json=bad_dur)
    assert resp.status_code == 422
    assert "Duration must be between 1.0 and 60.0 seconds" in str(resp.json())


def test_api_verification(client):
    """Verify GET /api/verification runs all 3 automated checks and reports all passed."""
    resp = client.get("/api/verification")
    assert resp.status_code == 200
    data = resp.json()
    assert data["all_passed"] is True
    checks = data["checks"]
    assert checks["q15_vs_float"]["passed"] is True
    assert checks["arm_vs_python"]["passed"] is True
    assert checks["cache_vs_hand_calc"]["passed"] is True


def test_api_traceability(client):
    """Verify GET /api/traceability returns parsed CO mapping and dimensions."""
    resp = client.get("/api/traceability")
    assert resp.status_code == 200
    data = resp.json()
    assert "course_outcomes" in data
    assert "dimensions" in data
    assert len(data["course_outcomes"]) == 6
    assert len(data["dimensions"]) == 2
    # Verify placeholder replacement
    first_co = data["course_outcomes"][0]
    assert "To be confirmed from the syllabus" in first_co["Official Syllabus Description"]


def test_api_frontend_static_serving(client):
    """Verify that the frontend files (HTML, CSS, JS) are properly mounted and served."""
    # Test index.html served at root
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert "Wearable Health-Monitoring ARM System" in resp.text
    assert "id=\"waveform-chart\"" in resp.text

    # Test styles.css
    resp_css = client.get("/styles.css")
    assert resp_css.status_code == 200
    assert "text/css" in resp_css.headers.get("content-type", "")
    assert "--accent-blue" in resp_css.text

    # Test app.js
    resp_js = client.get("/app.js")
    assert resp_js.status_code == 200
    assert "javascript" in resp_js.headers.get("content-type", "")
    assert "runSimulation" in resp_js.text



