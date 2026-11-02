# Frontend Interactive Dashboard

The interactive educational dashboard for the **Wearable Health-Monitoring ARM System** mini-project. It allows students, instructors, and examiners to simulate, inspect, and evaluate an energy-conscious ARM Cortex-M processor pipeline for physiological signal monitoring in real time.

---

## 📸 Screenshots

| Light Mode Dashboard | Dark Mode Dashboard |
| :---: | :---: |
| *[Screenshot Placeholder: Light Mode Dashboard showing KPI cards, controls, waveform chart, and Q15 Number Representation]* | *[Screenshot Placeholder: Dark Mode Dashboard showing ARM instruction stepper and ALU flags]* |

| ARM Cortex-M Instruction Stepper | Cache Address Slicing & AMAT |
| :---: | :---: |
| *[Screenshot Placeholder: Unicorn ARM Thumb 18-step opcode execution and R0–R7 register file]* | *[Screenshot Placeholder: 32-bit address partitioning bar (Tag, Index, Offset) and AMAT comparison]* |

---

## 🛠️ Architecture & Design Principles

- **Zero Build Step:** Built with standards-compliant HTML5, modern CSS3 (Custom Properties & Flexbox/Grid), and Vanilla ES6+ JavaScript. No Node.js build tools, Webpack, or framework compilation required.
- **Direct FastAPI Static Mount:** Automatically served at `http://localhost:8000/` by FastAPI's `StaticFiles` middleware in `backend/api.py`.
- **Strict Hard Constraints Compliance:**
  - **No Invented Numbers:** All displayed metrics, figures, and charts are populated exclusively from live REST responses (`/api/run`, `/api/verification`, `/api/traceability`, `/api/defaults`).
  - **Datasheet Placeholder Banners:** When unverified STM32L476RG datasheet parameters are in effect, prominent `⚠️ PLACEHOLDER` alert banners and badges appear automatically.
  - **Syllabus Traceability:** Wording for course outcomes (CO1–CO6) and evaluation dimensions (CT + RWE) is loaded dynamically from `docs/CO_MAPPING.md` and `docs/DIMENSION.md`. If unconfirmed by the student, the UI displays *"To be confirmed from the syllabus"*.
- **Accessibility & Polish:**
  - WCAG AA compliant color contrast ratios across light and dark themes.
  - Full keyboard navigability with visible focus indicators (`:focus-visible`).
  - Responsive design supporting mobile viewports, tablets, and desktop displays without horizontal scrolling.
  - Status indicators use explicit text and iconography (never color alone).
- **External Dependencies:**
  - [Chart.js v4.4.1](https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js) loaded via pinned CDN for hardware-accelerated HTML5 canvas rendering.

---

## 📁 File Structure

```text
frontend/
├── index.html        # Semantic HTML5 document (header, controls, KPIs, canvas, 8 tabs, tour modal)
├── styles.css        # Responsive CSS styling with dark/light CSS custom properties & WCAG AA contrast
├── app.js            # Vanilla JavaScript controller (REST client, Chart.js, ARM stepper, tour state)
└── README.md         # Frontend technical guide and documentation
```

---

## 🚀 How to Run

1. Ensure the Python virtual environment is activated and requirements are installed:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Start the FastAPI backend server:
   ```powershell
   python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Open your web browser and navigate to:
   ```text
   http://localhost:8000
   ```

4. The dashboard will load immediately, perform a health check (`GET /api/health`), retrieve configuration defaults (`GET /api/defaults`), and execute an initial baseline simulation run (`POST /api/run`).

---

## 🧭 Dashboard Features & COA Concept Walkthrough

### 1. Header & Navigation
- **Connection Status Chip:** Displays real-time status of the backend API (`Backend Online` / `Backend Offline`). Automatically re-checks every 10 seconds.
- **🗺️ Start Tour:** Opens a 5-step interactive walkthrough explaining the complete signal path from sensor acquisition to energy-saving sleep modes.
- **📥 Export:**
  - `Export Run (JSON)`: Downloads the complete simulation result payload (`wearable_arm_simulation.json`).
  - `Export Signal (CSV)`: Downloads a high-resolution CSV table (`time_s,raw_adc,q15,filtered_q15,is_systolic_peak`) for external verification.
- **🌙 / ☀️ Theme Toggle:** Toggles between accessible dark and light themes, persisting the preference in `localStorage`.

### 2. Parameter Controls Panel
- **Signal Source:** Choose between clinical records (*PhysioNet BIDMC 125 Hz*) or the offline *Deterministic Synthetic Generator*.
- **Alert Threshold (BPM):** Adjust safety limit [40–220 BPM] with synchronized slider and numeric input.
- **Duration (sec):** Select analysis window [1–60 s]. Automatically downsamples signals $>20\text{ s}$ for smooth rendering.
- **Cache Geometry:** Select Cache Size (64 B to 64 KB), Line Size (4 B to 128 B), and Associativity (Direct-Mapped, 2/4/8-Way).
- **Active Time (%):** Set CPU duty cycle [0.1% to 100.0%].

### 3. KPI Summary Cards
- **Heart Rate (BPM):** Classical peak detection extraction (no ML) with `NORMAL` or `ALERT (TACHYCARDIA)` badges.
- **ALU Alert Branch:** Displays `BGT: YES` or `BGT: NO` along with live APSR status flags (`N`, `Z`, `C`, `V`).
- **Cache Performance & AMAT:** Reports hit rate (%) and Average Memory Access Time compared to un-cached Flash (20.0 cycles).
- **Average Current Draw:** Reports duty-cycled current (&mu;A) and percentage energy savings vs. continuous Run mode.

### 4. Real-Time Physiological Waveform Canvas
- Renders raw 12-bit ADC integers, ARM-filtered Q15 samples, and detected systolic pulse peaks on a dual-axis canvas.
- Toggle visibility of individual signal layers using the interactive legend checkboxes.

### 5. Concept Subsystem Tabs
- **Tab 1: Number Representation (CO1):** Shows the last sample as raw 12-bit ADC decimal and hex, signed Q15 decimal and hex, and ARM filtered output with worked conversion examples.
- **Tab 2: ALU & Status Flags (CO2):** Illustrates how 32-bit subtraction (`CMP bpm, threshold`) sets APSR condition flags (`N`, `Z`, `C`, `V`) with interactive LED indicators and evaluates `BGT` condition `(Z == 0) && (N == V)`.
- **Tab 3: ARM Core & Registers (CO3):** 18-step interactive stepper through the genuine Thumb moving average routine running in the Unicorn emulator. Inspects low registers `R0`–`R7` with register-change highlighting and verifies 100% bit-exact equivalence with Python.
- **Tab 4: Cache Hierarchy (CO4):** Visualizes 32-bit address partitioning into Tag, Index, and Offset slices, and computes hit rate, miss rate, and AMAT.
- **Tab 5: Serial Interconnects (CO5):** Analyzes UART (8-N-1 at 115,200 baud) and I2C (100 kHz Standard Mode) bus timings, frame structures, and channel utilisation.
- **Tab 6: Duty-Cycle Energy Model (CO6):** Formulates average current draw $I_{\text{avg}} = I_{\text{active}} \times D + I_{\text{sleep}} \times (1 - D)$ using STM32L476RG datasheet values, showing >90% battery savings.
- **Tab 7: Automated Verification Suite:** Live architectural validation cards querying `GET /api/verification`: Q15 quantization error, ARM emulator vs. Python reference, and Cache simulator vs. hand calculation.
- **Tab 8: Traceability (CO1–CO6 & Dimensions):** Live rendering of syllabus outcomes and evaluation dimensions directly from `docs/CO_MAPPING.md` and `docs/DIMENSION.md`.
