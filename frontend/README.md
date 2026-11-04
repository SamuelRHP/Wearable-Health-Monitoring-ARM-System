# Frontend Interactive Dashboard

The interactive educational dashboard for the **Wearable Health-Monitoring ARM System** mini-project. It allows students, instructors, and examiners to simulate, inspect, and evaluate an energy-conscious ARM Cortex-M processor pipeline for physiological signal monitoring in real time.

---

## 📸 Screenshots

| Light Mode Demo View | Dark Mode Demo View |
| :---: | :---: |
| *[Screenshot Placeholder: Light Mode Demo View showing 3 controls, presets, pipeline strip, KPI cards, and waveform chart]* | *[Screenshot Placeholder: Dark Mode Demo View showing Tachycardia Alert, ALU flags, and high-contrast projector layout]* |

| ARM Cortex-M Instruction Stepper (Details) | Cache Address Slicing & AMAT (Details) |
| :---: | :---: |
| *[Screenshot Placeholder: Unicorn ARM Thumb 18-step opcode execution and R0–R7 register file]* | *[Screenshot Placeholder: 32-bit address partitioning bar (Tag, Index, Offset) and AMAT comparison]* |

---

## 🎬 In-Person Live Demo Script (2-Minute Teacher Walkthrough)

Follow this step-by-step walkthrough when presenting live in person to your teacher or examiner. The dashboard starts on the clean **Demo View** with high-contrast projector styling and zero scrolling on a standard 1366×768 screen.

| Step | Time | What to Do | What Happens on Screen | What to Say to the Teacher |
| :---: | :---: | :--- | :--- | :--- |
| **1** | **0:00 – 0:20** | **Open Dashboard**<br>`http://localhost:8000` | • Status chip: `● Backend Online`<br>• Demo View loads with 3 plain controls<br>• Baseline normal simulation runs automatically<br>• Horizontal pipeline ribbon displays live values across all 6 stages | *"This is an energy-conscious ARM Cortex-M processor simulation for continuous physiological health monitoring. We model the full hardware chain from 12-bit ADC up to duty-cycled low-power sleep modes."* |
| **2** | **0:20 – 0:40** | **Show Normal Rhythm**<br>Click `⚡ Normal (75 bpm, threshold 100)` | • Controls set: Threshold 100 BPM, Active 5.0%, Cache 4 KB<br>• Waveform displays 12-bit ADC & filtered Q15<br>• Heart Rate: `75 BPM` (`NORMAL` badge)<br>• ALU branch: `BGT: NO`<br>• Cache hit rate: `>99%`<br>• Energy savings: `~95%` | *"At normal resting cardiac rate (~75 BPM), heart rate is safely below our 100 BPM threshold. The ALU computes 75 minus 100, which is negative, so the BGT conditional branch is not taken. Notice our duty cycle: the core sleeps 95% of the time, saving 95% energy."* |
| **3** | **0:40 – 1:05** | **Trigger Tachycardia Alert**<br>Click `🚨 Trigger alert (thresh 70)` | • Threshold immediately adjusts to 70 BPM<br>• Simulation re-runs in <100 ms<br>• Card turns red: `ALERT (TACHYCARDIA)`<br>• ALU branch switches to `BGT: YES (ALERT)`<br>• APSR flags: `N` clears, `C` asserts (`Z=0, N=V=0`)<br>• Red systolic peak markers remain visible | *"Now I lower the threshold to 70 BPM with one click. The ALU subtraction (75 - 70 = +5) clears the Negative flag and sets Carry. In ARM Cortex-M, condition GT is (Z==0 && N==V), which evaluates to TRUE. The branch is taken and an emergency alert is triggered!"* |
| **4** | **1:05 – 1:30** | **Explain Pipeline Ribbon**<br>Point to the 6 horizontal steps | • Step 1: `ADC: 2048 → Q15: 0x0000`<br>• Step 2: `ARM Routine (100% Match)`<br>• Step 3: `ALU CMP (APSR Flags & BGT)`<br>• Step 4: `Cache (AMAT: 1.01 cyc vs 20 cyc)`<br>• Step 5: `Serial I/O (UART 8.7% & I2C 6.0%)`<br>• Step 6: `Energy (421 µA, 95% Saved)` | *"This horizontal strip traces the live hardware pipeline across all 6 course outcomes: 12-bit ADC converts to signed Q15 without software division, genuine Thumb instructions execute the 4-tap boxcar filter in Unicorn, ALU flags drive the branch, cache reduces AMAT from 20 to 1 cycle, and serial bus load is under 9%, enabling 95% sleep."* |
| **5** | **1:30 – 1:55** | **Deep-Dive into Details**<br>Click `🔍 Details View` $\to$ `🧠 3. ARM Core & Stepper` | • Switches to Details view<br>• Displays the 18 Thumb instructions in `asm/moving_average.s`<br>• Shows low register file $R0$–$R7$ and APSR flags<br>• Click `Next ▶` to step through instructions | *"If we click into the Details view, here is our 18-step ARM Thumb assembly debugger running on the Unicorn emulator. We can step through instruction by instruction—loading halfwords with LDRH, sign-extending with SXTH, and arithmetic right shifting with ASRS #2—verifying 100% bit-exact equivalence with Python."* |
| **6** | **1:55 – 2:00** | **Return to Demo**<br>Click `⬅ Return to Demo View` | • Instantly returns to the clean Demo view<br>• Ready for examiner questions | *"Everything is available under Details, but the main Demo view provides our complete real-time operating picture."* |

---

## 🛠️ Architecture & Design Principles

- **Dual-View Navigation:**
  - **Demo View (Default):** Clean presenter layout optimized for 1366×768 projectors without vertical scrolling. Shows 3 plain controls, two 1-click presets, a 6-stage hardware pipeline ribbon, 4 summary cards, and the waveform canvas.
  - **Details View:** Accessible from the `🔍 Details View` button. Houses all 7 COA subsystem concept tabs, full controls, the interactive ARM register stepper, verification cards, guided tour, and JSON/CSV export actions.
- **Zero Build Step:** Built with standards-compliant HTML5, modern CSS3 (Custom Properties & Flexbox/Grid), and Vanilla ES6+ JavaScript. No Node.js build tools, Webpack, or framework compilation required.
- **Direct FastAPI Static Mount:** Automatically served at `http://localhost:8000/` by FastAPI's `StaticFiles` middleware in `backend/api.py`.
- **Strict Hard Constraints Compliance:**
  - **No Invented Numbers:** All displayed metrics, figures, and charts are populated exclusively from live REST responses (`/api/run`, `/api/verification`, `/api/traceability`, `/api/defaults`).
  - **Shrunk Datasheet Placeholder Chip:** Unverified STM32L476RG datasheet parameters are identified by an unobtrusive chip next to the energy card (`Estimates (placeholder) ℹ️`) with an informative tooltip, keeping the presenter screen uncluttered.
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
├── index.html        # Semantic HTML5 document (Demo view + Details view, 8 tabs, tour modal)
├── styles.css        # Responsive CSS styling with dark/light variables & 1366x768 projector layout
├── app.js            # Vanilla JavaScript controller (view switching, presets, Chart.js, ARM stepper)
└── README.md         # Frontend technical guide and demo script
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

4. The dashboard will load directly on the **Demo View**, perform a health check (`GET /api/health`), retrieve configuration defaults (`GET /api/defaults`), and execute an initial baseline simulation run (`POST /api/run`).

---

## 🧭 Dashboard Views & Features Walkthrough

### 1. Demo View (Presenter-Friendly Default)
- **Top Controls:** Three plain-language controls:
  - **Alert Threshold (BPM):** Slider + number input [40–220 BPM] (default: 100 BPM).
  - **Core Active Time (%):** Slider + number input [0.1–100.0%] (default: 5.0%).
  - **Cache Size (Bytes):** Dropdown covering powers of 2 from 64 B to 64 KB (default: 4 KB).
- **Actions & Presets:**
  - `▶ Run Simulation` (large primary button with loading spinner)
  - `🔄 Reset` (reverts all controls to defaults)
  - `⚡ Normal (75 bpm, thresh 100)` (1-click preset)
  - `🚨 Trigger alert (thresh 70)` (1-click preset)
- **Horizontal Pipeline Strip:** 6 connected stages updating live on every run:
  1. *ADC &rarr; Q15:* Shows last sample ADC integer and Q15 hex mapping.
  2. *ARM Routine:* Shows boxcar moving average and 100% Python match confirmation.
  3. *ALU & Flags:* Displays live APSR flags ($N, Z, C, V$) and BGT branch decision.
  4. *Cache Memory:* Displays hit rate percentage and AMAT in cycles.
  5. *Serial I/O:* Displays UART and I2C channel utilisation at 125 Hz.
  6. *Energy Model:* Displays average current draw and percentage power savings.
  *(Tip: Clicking any pipeline stage opens that concept tab in Details view!)*
- **Four Summary Cards:**
  1. *Heart Rate:* Classical peak detection extraction (no ML) with `NORMAL` or `ALERT` badge.
  2. *Alert Status & ALU:* Displays BGT branch status and live APSR flag indicators.
  3. *Cache Hit Rate & AMAT:* Reports hit rate (%) and Average Memory Access Time compared to un-cached Flash (20.0 cycles).
  4. *Average Current:* Reports duty-cycled current (&mu;A), percentage energy savings, and the small placeholder tooltip chip.
- **Waveform Canvas:** Dual-axis Chart.js graph rendering 12-bit ADC integers, ARM-filtered Q15 samples, and detected systolic pulse peaks.

### 2. Details View (`🔍 Details View`)
Accessible at any time via the header view switcher button:
- **Full Controls Panel:** Configure Signal Source (`Synthetic`, `bidmc01`, `bidmc02`), Simulated Heart Rate (40–180 BPM for synthetic mode), Alert Threshold, Duration (1–60s), Cache parameters, and Duty-cycle Active Fraction.
- **Dedicated Real-Time Physiological Waveform:** Interactive Chart.js graph rendering 12-bit ADC raw samples, signed Q15 samples, and detected systolic pulse peaks directly inside the Details view, updating live on every run.
- **Tab 1: Number Representation (CO1):** Shows the last sample as raw 12-bit ADC decimal and hex, signed Q15 decimal and hex, and ARM filtered output with worked conversion examples.
- **Tab 2: ALU & Status Flags (CO2):** Illustrates how 32-bit subtraction (`CMP bpm, threshold`) sets APSR condition flags (`N`, `Z`, `C`, `V`) with interactive LED indicators and evaluates `BGT` condition `(Z == 0) && (N == V)`.
- **Tab 3: ARM Core & Registers (CO3):** 18-step interactive stepper through the genuine Thumb moving average routine running in the Unicorn emulator. Inspects low registers `R0`–`R7` with register-change highlighting and verifies 100% bit-exact equivalence with Python.
- **Tab 4: Cache Hierarchy (CO4):** Visualizes 32-bit address partitioning into Tag, Index, and Offset slices, and computes hit rate, miss rate, and AMAT.
- **Tab 5: Serial Interconnects (CO5):** Analyzes UART (8-N-1 at 115,200 baud) and I2C (100 kHz Standard Mode) bus timings, frame structures, and channel utilisation.
- **Tab 6: Duty-Cycle Energy Model (CO6):** Formulates average current draw $I_{\text{avg}} = I_{\text{active}} \times D + I_{\text{sleep}} \times (1 - D)$ using STM32L476RG datasheet values, showing >90% battery savings.
- **Tab 7: Automated Verification Suite:** Live architectural validation cards querying `GET /api/verification`: Q15 quantization error, ARM emulator vs. Python reference, and Cache simulator vs. hand calculation.
