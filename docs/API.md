# Backend REST API Specification

**Service:** Wearable Health-Monitoring ARM System  
**Framework:** FastAPI (Python 3.10+)  
**Default Host & Port:** `http://localhost:8000`  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI) / `http://localhost:8000/redoc`  
**CORS Policy:** Allowed for all `localhost` and `127.0.0.1` origins.

---

## 1. System Health Check
Check operational status of the API server.

- **Method:** `GET`
- **Path:** `/api/health`
- **Response `200 OK`:**
```json
{
  "status": "ok"
}
```

---

## 2. Default Parameters & Validation Ranges
Retrieve default simulation tunables, allowable parameter ranges for validation, and active placeholder warnings.

- **Method:** `GET`
- **Path:** `/api/defaults`
- **Response `200 OK`:**
```json
{
  "defaults": {
    "source": "synthetic",
    "threshold_bpm": 100.0,
    "cache_size_bytes": 4096,
    "line_size_bytes": 16,
    "associativity": 1,
    "active_fraction": 0.05,
    "duration_s": 10.0,
    "fs_hz": 125.0
  },
  "validation_ranges": {
    "threshold_bpm": {"min": 40.0, "max": 220.0, "description": "Heart rate alert threshold in BPM"},
    "duration_s": {"min": 1.0, "max": 60.0, "description": "Simulation window duration in seconds"},
    "cache_size_bytes": {"min": 64, "max": 65536, "description": "Cache capacity in bytes"},
    "line_size_bytes": {"min": 4, "max": 128, "description": "Cache line size in bytes"},
    "associativity": {"min": 1, "max": 16, "description": "Cache associativity"},
    "active_fraction": {"min": 0.001, "max": 1.0, "description": "Processor active duty cycle fraction"}
  },
  "placeholders": {
    "energy_parameters": true,
    "warning": "WARNING: Energy parameters are unverified PLACEHOLDER values pending datasheet confirmation by student (see docs/OPEN_ITEMS.md). Results are estimated from manufacturer datasheets; never claim real battery life.",
    "target_mcu": "STM32L476RG",
    "source": {
      "name": "STMicroelectronics STM32L476xx Datasheet (DocID025976 Rev 5)",
      "url": "https://www.st.com/resource/en/datasheet/stm32l476rg.pdf",
      "section": "Table 34 & Table 39",
      "page": "112, 120",
      "status": "PLACEHOLDER"
    }
  }
}
```

---

## 3. Available Signal Records
Query available physiological signal sources.

- **Method:** `GET`
- **Path:** `/api/records`
- **Response `200 OK`:**
```json
[
  "bidmc01",
  "bidmc02",
  "synthetic"
]
```

---

## 4. Run Simulation Pipeline
Run the full-pipeline physiological monitor and return all integrated Computer Organization and Architecture metrics.

- **Method:** `POST`
- **Path:** `/api/run`
- **Request Headers:** `Content-Type: application/json`
- **Request Body JSON:**
```json
{
  "source": "synthetic",
  "threshold_bpm": 100.0,
  "cache_size_bytes": 4096,
  "line_size_bytes": 16,
  "associativity": 1,
  "active_fraction": 0.05,
  "duration_s": 10.0
}
```

- **Validation Error `422 Unprocessable Entity` (Plain Language):**
```json
{
  "detail": [
    "Parameter 'body -> threshold_bpm': Threshold must be between 40.0 and 220.0 BPM (physiological limits)"
  ]
}
```

- **Response `200 OK` (Schema Final Contract):**
```json
{
  "meta": {
    "source": "synthetic",
    "fs_hz": 125.0,
    "duration_s": 10.0,
    "placeholders_in_use": true,
    "warnings": [
      "WARNING: Energy parameters are unverified PLACEHOLDER values pending datasheet confirmation by student (see docs/OPEN_ITEMS.md). Results are estimated from manufacturer datasheets; never claim real battery life."
    ]
  },
  "signal": {
    "raw_adc": [2048, 2062, 2095],
    "q15": [0, 224, 752],
    "filtered_q15": [0, 224, 752],
    "peaks": [93, 218, 343, 468, 593, 718, 843, 968, 1093, 1218]
  },
  "heart_rate": {
    "bpm": 75.0,
    "alert": false
  },
  "number_repr": {
    "last_sample": {
      "adc": 2048,
      "adc_hex": "0x800",
      "q15": 0,
      "q15_hex": "0x0000",
      "filtered": 0,
      "filtered_hex": "0x0000"
    }
  },
  "alu": {
    "result": 4294967271,
    "flags": {
      "N": true,
      "Z": false,
      "C": false,
      "V": false
    },
    "branch_taken": false
  },
  "serial": {
    "uart": {
      "baud": 115200,
      "bytes_per_s": 1000.0,
      "packet_bytes": 8,
      "utilisation_pct": 8.6806
    },
    "i2c": {
      "clock_hz": 100000,
      "transaction_us": 480.0,
      "utilisation_pct": 6.0
    }
  },
  "arm": {
    "steps": [
      {
        "instruction": "ldrh r2, [r0, #0]",
        "registers": {
          "r0": 131072, "r1": 10000, "r2": 0, "r3": 0,
          "r4": 0, "r5": 0, "r6": 0, "r7": 0
        },
        "flags": {"N": false, "Z": false, "C": false, "V": false}
      }
    ],
    "matches_python": true
  },
  "cache": {
    "hit_rate": 0.9995,
    "miss_rate": 0.0005,
    "amat_cycles": 1.01,
    "amat_no_cache_cycles": 20.0,
    "geometry": {
      "lines": 256,
      "offset_bits": 4,
      "index_bits": 8,
      "tag_bits": 20
    }
  },
  "energy": {
    "avg_current_ua": 421.14,
    "always_on_ua": 8400.0,
    "saving_pct": 94.9864,
    "placeholder": true,
    "source": "STMicroelectronics STM32L476xx Datasheet (DocID025976 Rev 5) (Page 112, 120, https://www.st.com/resource/en/datasheet/stm32l476rg.pdf)"
  }
}
```

---

## 5. Automated Verification Results
Query the 3 automated architectural verification suites.

- **Method:** `GET`
- **Path:** `/api/verification`
- **Response `200 OK`:**
```json
{
  "all_passed": true,
  "checks": {
    "q15_vs_float": {
      "name": "Q15 vs Float Reference",
      "passed": true,
      "max_absolute_error": 1.52587890625e-05,
      "mean_absolute_error": 7.421875e-06,
      "rmse": 8.7890625e-06,
      "snr_db": 91.24
    },
    "arm_vs_python": {
      "name": "Emulated ARM vs Pure Python",
      "passed": true,
      "vectors_tested": 100,
      "matches_python": true,
      "mismatches": 0
    },
    "cache_vs_hand_calc": {
      "name": "Cache Simulator vs Hand Calculation",
      "passed": true,
      "total_accesses": 10,
      "expected_hits": 7,
      "actual_hits": 7,
      "hit_rate": 0.7,
      "amat_cycles": 7.0
    }
  }
}
```

---

## 6. Course Traceability & Dimension Mapping
Retrieve parsed Course Outcomes (CO1-CO6) and dimension tracking from `docs/CO_MAPPING.md` and `docs/DIMENSION.md`. If unconfirmed by student, descriptions default to `"To be confirmed from the syllabus"`.

- **Method:** `GET`
- **Path:** `/api/traceability`
- **Response `200 OK`:**
```json
{
  "course_outcomes": [
    {
      "Course Outcome": "CO1",
      "Official Syllabus Description": "To be confirmed from the syllabus",
      "COA Concept Demonstrated": "Data Representation & Computer Arithmetic...",
      "Implementation Module": "`sim/q15.py`",
      "Automated Test File": "`tests/test_q15.py`",
      "Proposed UI Tab (Frontend)": "*Tab 1: Number Representation*",
      "Student Confirmation": "[ ] Pending Confirmation"
    }
  ],
  "dimensions": [
    {
      "Dimension": "CT",
      "Full Name": "To be confirmed from the syllabus",
      "Official Rubric Description": "To be confirmed from the syllabus",
      "How Demonstrated in Project": "Decomposition & Algorithmic Rigor...",
      "Primary Modules & Verification": "`sim/q15.py`...",
      "Student Confirmation": "[ ] Pending Confirmation"
    }
  ],
  "co_file": "docs/CO_MAPPING.md",
  "dim_file": "docs/DIMENSION.md"
}
```

