/**
 * Wearable Health-Monitoring ARM System — Interactive COA Dashboard
 * 
 * Frontend Client Application
 * ----------------------------
 * Integrates directly with the FastAPI backend at http://localhost:8000:
 * - Real-time REST API integration with /api/health, /api/defaults, /api/run,
 *   /api/verification, and /api/traceability.
 * - Dynamic physiological waveform visualization via Chart.js with peak marking.
 * - Step-through ARM Cortex-M Thumb register file inspection (R0–R7, APSR flags).
 * - Full coverage of COA subsystems: Number representation (Q15), ALU flags,
 *   ARM instruction execution, Cache hierarchy & AMAT, Serial I/O, Duty-cycle energy.
 * - WCAG AA accessible, dark/light theme toggle, and client-side JSON/CSV export.
 */

"use strict";

// ============================================================================
// State Management
// ============================================================================

const state = {
  backendOnline: false,
  defaults: null,
  lastResult: null,
  armStepIndex: 0,
  tourCurrentStep: 0,
  chartInstance: null,
  verificationData: null,
  traceabilityData: null,
  theme: "dark", // default
};

// ============================================================================
// DOM Element Selectors
// ============================================================================

const dom = {
  // Header & Status
  backendStatus: document.getElementById("backend-status"),
  backendStatusText: document.getElementById("backend-status-text"),
  btnTour: document.getElementById("btn-tour"),
  btnExportDropdown: document.getElementById("btn-export-dropdown"),
  exportMenu: document.getElementById("export-menu"),
  btnExportJson: document.getElementById("btn-export-json"),
  btnExportCsv: document.getElementById("btn-export-csv"),
  themeToggle: document.getElementById("theme-toggle"),

  // Banners
  placeholderBanner: document.getElementById("placeholder-banner"),
  placeholderBannerText: document.getElementById("placeholder-banner-text"),
  globalErrorBanner: document.getElementById("global-error-banner"),
  globalErrorText: document.getElementById("global-error-text"),
  btnCloseError: document.getElementById("btn-close-error"),

  // Form Controls
  ctrlSource: document.getElementById("ctrl-source"),
  ctrlThreshold: document.getElementById("ctrl-threshold"),
  ctrlThresholdNum: document.getElementById("ctrl-threshold-num"),
  ctrlDuration: document.getElementById("ctrl-duration"),
  ctrlDurationNum: document.getElementById("ctrl-duration-num"),
  ctrlCacheSize: document.getElementById("ctrl-cache-size"),
  ctrlLineSize: document.getElementById("ctrl-line-size"),
  ctrlAssociativity: document.getElementById("ctrl-associativity"),
  ctrlActiveFrac: document.getElementById("ctrl-active-frac"),
  ctrlActiveFracNum: document.getElementById("ctrl-active-frac-num"),
  btnRunSim: document.getElementById("btn-run-sim"),
  btnResetDefaults: document.getElementById("btn-reset-defaults"),
  simSpinner: document.getElementById("sim-spinner"),
  btnRunText: document.getElementById("btn-run-text"),

  // KPI Summary Cards
  kpiHrVal: document.getElementById("kpi-hr-val"),
  kpiAlertBadge: document.getElementById("kpi-alert-badge"),
  kpiBranchVal: document.getElementById("kpi-branch-val"),
  chipFlagN: document.getElementById("chip-flag-n"),
  chipFlagZ: document.getElementById("chip-flag-z"),
  chipFlagC: document.getElementById("chip-flag-c"),
  chipFlagV: document.getElementById("chip-flag-v"),
  kpiCacheVal: document.getElementById("kpi-cache-val"),
  kpiAmatVal: document.getElementById("kpi-amat-val"),
  kpiEnergyVal: document.getElementById("kpi-energy-val"),
  kpiSavingsBadge: document.getElementById("kpi-savings-badge"),

  // Chart Canvas & Toggles
  waveformChart: document.getElementById("waveform-chart"),
  chkShowAdc: document.getElementById("chk-show-adc"),
  chkShowFiltered: document.getElementById("chk-show-filtered"),
  chkShowPeaks: document.getElementById("chk-show-peaks"),

  // Tabs Navigation & Panels
  tabButtons: document.querySelectorAll(".tab-btn"),
  tabPanels: document.querySelectorAll(".tab-panel"),

  // Tab 1: Number Representation
  numLastAdc: document.getElementById("num-last-adc"),
  numLastAdcHex: document.getElementById("num-last-adc-hex"),
  numLastQ15: document.getElementById("num-last-q15"),
  numLastQ15Hex: document.getElementById("num-last-q15-hex"),
  numLastFiltered: document.getElementById("num-last-filtered"),
  numLastFilteredHex: document.getElementById("num-last-filtered-hex"),

  // Tab 2: ALU
  ledFlagN: document.getElementById("led-flag-n"),
  ledFlagZ: document.getElementById("led-flag-z"),
  ledFlagC: document.getElementById("led-flag-c"),
  ledFlagV: document.getElementById("led-flag-v"),
  aluResultVal: document.getElementById("alu-result-val"),
  aluResultHex: document.getElementById("alu-result-hex"),
  aluBranchEval: document.getElementById("alu-branch-eval"),

  // Tab 3: ARM Core & Stepper
  armMatchBadge: document.getElementById("arm-match-badge"),
  btnStepFirst: document.getElementById("btn-step-first"),
  btnStepPrev: document.getElementById("btn-step-prev"),
  btnStepNext: document.getElementById("btn-step-next"),
  btnStepLast: document.getElementById("btn-step-last"),
  stepCounterText: document.getElementById("step-counter-text"),
  activeInstrCode: document.getElementById("active-instr-code"),
  regVals: {
    r0: document.getElementById("reg-val-r0"),
    r1: document.getElementById("reg-val-r1"),
    r2: document.getElementById("reg-val-r2"),
    r3: document.getElementById("reg-val-r3"),
    r4: document.getElementById("reg-val-r4"),
    r5: document.getElementById("reg-val-r5"),
    r6: document.getElementById("reg-val-r6"),
    r7: document.getElementById("reg-val-r7"),
  },
  regBoxes: {
    r0: document.getElementById("reg-box-r0"),
    r1: document.getElementById("reg-box-r1"),
    r2: document.getElementById("reg-box-r2"),
    r3: document.getElementById("reg-box-r3"),
    r4: document.getElementById("reg-box-r4"),
    r5: document.getElementById("reg-box-r5"),
    r6: document.getElementById("reg-box-r6"),
    r7: document.getElementById("reg-box-r7"),
  },

  // Tab 4: Cache Hierarchy
  bitTagCount: document.getElementById("bit-tag-count"),
  bitIndexCount: document.getElementById("bit-index-count"),
  bitOffsetCount: document.getElementById("bit-offset-count"),
  chunkTag: document.getElementById("chunk-tag"),
  chunkIndex: document.getElementById("chunk-index"),
  chunkOffset: document.getElementById("chunk-offset"),
  cacheHitrateVal: document.getElementById("cache-hitrate-val"),
  cacheMissrateVal: document.getElementById("cache-missrate-val"),
  cacheAmatVal: document.getElementById("cache-amat-val"),

  // Tab 5: Serial Interconnects
  uartBaud: document.getElementById("uart-baud"),
  uartMaxBps: document.getElementById("uart-max-bps"),
  uartUtil: document.getElementById("uart-util"),
  i2cClock: document.getElementById("i2c-clock"),
  i2cLatency: document.getElementById("i2c-latency"),
  i2cUtil: document.getElementById("i2c-util"),

  // Tab 6: Duty-Cycle Energy
  energyTabAvg: document.getElementById("energy-tab-avg"),
  energyTabBase: document.getElementById("energy-tab-base"),
  energyTabSavings: document.getElementById("energy-tab-savings"),
  energySourceText: document.getElementById("energy-source-text"),

  // Tab 7: Verification Suite
  verifyQ15Mae: document.getElementById("verify-q15-mae"),
  verifyQ15Mean: document.getElementById("verify-q15-mean"),
  verifyQ15Rmse: document.getElementById("verify-q15-rmse"),
  verifyQ15Snr: document.getElementById("verify-q15-snr"),
  badgeVerifyQ15: document.getElementById("badge-verify-q15"),
  iconVerifyQ15: document.getElementById("icon-verify-q15"),

  verifyArmVectors: document.getElementById("verify-arm-vectors"),
  verifyArmMismatches: document.getElementById("verify-arm-mismatches"),
  badgeVerifyArm: document.getElementById("badge-verify-arm"),
  iconVerifyArm: document.getElementById("icon-verify-arm"),

  verifyCacheHits: document.getElementById("verify-cache-hits"),
  verifyCacheHitrate: document.getElementById("verify-cache-hitrate"),
  verifyCacheAmat: document.getElementById("verify-cache-amat"),
  badgeVerifyCache: document.getElementById("badge-verify-cache"),
  iconVerifyCache: document.getElementById("icon-verify-cache"),

  btnRetestVerification: document.getElementById("btn-retest-verification"),

  // Tab 8: Traceability
  tbodyCoMapping: document.getElementById("tbody-co-mapping"),
  tbodyDimensionMapping: document.getElementById("tbody-dimension-mapping"),

  // Guided Tour Modal
  tourModal: document.getElementById("tour-modal"),
  tourStepBadge: document.getElementById("tour-step-badge"),
  tourStepTitle: document.getElementById("tour-step-title"),
  tourStepBody: document.getElementById("tour-step-body"),
  btnTourClose: document.getElementById("btn-tour-close"),
  btnTourPrev: document.getElementById("btn-tour-prev"),
  btnTourNext: document.getElementById("btn-tour-next"),
};

// ============================================================================
// API Client Layer
// ============================================================================

const API_BASE = ""; // Relative path when served statically by FastAPI

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      let errorBody = {};
      try {
        errorBody = await res.json();
      } catch (_) {
        errorBody = { detail: res.statusText };
      }
      const err = new Error(res.statusText);
      err.status = res.status;
      err.detail = errorBody.detail || errorBody;
      throw err;
    }
    return await res.json();
  } catch (error) {
    if (!error.status) {
      error.isNetwork = true;
      error.detail = "Backend connection failed. Ensure the server is running on http://localhost:8000.";
    }
    throw error;
  }
}

// Check Backend Health
async function checkHealth() {
  try {
    const data = await fetchJson("/api/health");
    if (data.status === "ok") {
      setBackendStatus(true);
      return true;
    }
  } catch (_) {
    setBackendStatus(false);
    return false;
  }
}

function setBackendStatus(online) {
  state.backendOnline = online;
  if (online) {
    dom.backendStatus.className = "status-chip status-online";
    dom.backendStatusText.textContent = "Backend Online";
  } else {
    dom.backendStatus.className = "status-chip status-offline";
    dom.backendStatusText.textContent = "Backend Offline";
  }
}

// Display / Dismiss Error Alerts
function showErrorBanner(message) {
  dom.globalErrorText.textContent = message;
  dom.globalErrorBanner.style.display = "flex";
}

function hideErrorBanner() {
  dom.globalErrorBanner.style.display = "none";
}

// ============================================================================
// Initialization & Defaults Loading
// ============================================================================

async function initializeApp() {
  setupTheme();
  setupEventListeners();
  setupSliders();

  const isOnline = await checkHealth();
  if (isOnline) {
    await loadDefaultsAndSync();
    await runSimulation();
    await loadTraceability();
    await loadVerification();
  } else {
    showErrorBanner("Cannot connect to FastAPI backend at http://localhost:8000. Start it with: python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload");
  }

  // Periodic health check every 10 seconds
  setInterval(async () => {
    const wasOnline = state.backendOnline;
    const nowOnline = await checkHealth();
    if (!wasOnline && nowOnline) {
      hideErrorBanner();
      if (!state.lastResult) {
        await loadDefaultsAndSync();
        await runSimulation();
      }
    }
  }, 10000);
}

async function loadDefaultsAndSync() {
  try {
    const config = await fetchJson("/api/defaults");
    state.defaults = config;

    // Apply values to form controls
    const d = config.defaults;
    if (d) {
      dom.ctrlSource.value = d.source || "synthetic";
      dom.ctrlThreshold.value = d.threshold_bpm || 100;
      dom.ctrlThresholdNum.value = d.threshold_bpm || 100;
      dom.ctrlDuration.value = d.duration_s || 10;
      dom.ctrlDurationNum.value = d.duration_s || 10;
      dom.ctrlCacheSize.value = d.cache_size_bytes || 4096;
      dom.ctrlLineSize.value = d.line_size_bytes || 16;
      dom.ctrlAssociativity.value = d.associativity || 1;
      const activePct = (d.active_fraction * 100).toFixed(1);
      dom.ctrlActiveFrac.value = activePct;
      dom.ctrlActiveFracNum.value = activePct;
    }

    // Check placeholder warning status
    if (config.placeholders && config.placeholders.energy_parameters) {
      dom.placeholderBanner.style.display = "block";
      if (config.placeholders.warning) {
        dom.placeholderBannerText.textContent = config.placeholders.warning;
      }
    }
  } catch (err) {
    console.warn("Failed to load defaults from backend:", err);
  }
}

// Reset form to defaults
function resetToDefaults() {
  if (state.defaults) {
    const d = state.defaults.defaults;
    dom.ctrlSource.value = d.source || "synthetic";
    dom.ctrlThreshold.value = d.threshold_bpm || 100;
    dom.ctrlThresholdNum.value = d.threshold_bpm || 100;
    dom.ctrlDuration.value = d.duration_s || 10;
    dom.ctrlDurationNum.value = d.duration_s || 10;
    dom.ctrlCacheSize.value = d.cache_size_bytes || 4096;
    dom.ctrlLineSize.value = d.line_size_bytes || 16;
    dom.ctrlAssociativity.value = d.associativity || 1;
    const activePct = (d.active_fraction * 100).toFixed(1);
    dom.ctrlActiveFrac.value = activePct;
    dom.ctrlActiveFracNum.value = activePct;
  }
  hideErrorBanner();
}

// ============================================================================
// Form Event Handlers & Sliders
// ============================================================================

function setupSliders() {
  // Synchronize range sliders with number inputs
  function bindPair(slider, numberInput) {
    slider.addEventListener("input", () => {
      numberInput.value = slider.value;
    });
    numberInput.addEventListener("input", () => {
      const val = parseFloat(numberInput.value);
      const min = parseFloat(slider.min);
      const max = parseFloat(slider.max);
      if (!isNaN(val) && val >= min && val <= max) {
        slider.value = numberInput.value;
      }
    });
  }

  bindPair(dom.ctrlThreshold, dom.ctrlThresholdNum);
  bindPair(dom.ctrlDuration, dom.ctrlDurationNum);
  bindPair(dom.ctrlActiveFrac, dom.ctrlActiveFracNum);
}

function setupEventListeners() {
  // Run simulation button
  dom.btnRunSim.addEventListener("click", () => runSimulation());

  // Reset defaults button
  dom.btnResetDefaults.addEventListener("click", () => resetToDefaults());

  // Close global error alert
  dom.btnCloseError.addEventListener("click", () => hideErrorBanner());

  // Chart toggles
  dom.chkShowAdc.addEventListener("change", () => updateChartDatasetVisibility());
  dom.chkShowFiltered.addEventListener("change", () => updateChartDatasetVisibility());
  dom.chkShowPeaks.addEventListener("change", () => updateChartDatasetVisibility());

  // Tab switching
  dom.tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      switchTab(btn.getAttribute("aria-controls"));
    });
  });

  // Instruction Stepper Controls
  dom.btnStepFirst.addEventListener("click", () => stepARMInstruction("first"));
  dom.btnStepPrev.addEventListener("click", () => stepARMInstruction("prev"));
  dom.btnStepNext.addEventListener("click", () => stepARMInstruction("next"));
  dom.btnStepLast.addEventListener("click", () => stepARMInstruction("last"));

  // Verification Retest button
  dom.btnRetestVerification.addEventListener("click", () => loadVerification());

  // Tour controls
  dom.btnTour.addEventListener("click", () => openTour());
  dom.btnTourClose.addEventListener("click", () => closeTour());
  dom.btnTourNext.addEventListener("click", () => tourNext());
  dom.btnTourPrev.addEventListener("click", () => tourPrev());

  // Export dropdown
  dom.btnExportDropdown.addEventListener("click", (e) => {
    e.stopPropagation();
    const isExpanded = dom.exportMenu.classList.toggle("show");
    dom.btnExportDropdown.setAttribute("aria-expanded", isExpanded ? "true" : "false");
  });

  document.addEventListener("click", (e) => {
    if (!dom.btnExportDropdown.contains(e.target)) {
      dom.exportMenu.classList.remove("show");
      dom.btnExportDropdown.setAttribute("aria-expanded", "false");
    }
  });

  dom.btnExportJson.addEventListener("click", () => exportSimulationJson());
  dom.btnExportCsv.addEventListener("click", () => exportSignalCsv());

  // Theme Toggle
  dom.themeToggle.addEventListener("click", () => toggleTheme());
}

// ============================================================================
// Simulation Execution (POST /api/run)
// ============================================================================

async function runSimulation() {
  const activePercent = parseFloat(dom.ctrlActiveFrac.value);
  const activeFraction = activePercent / 100.0;

  const payload = {
    source: dom.ctrlSource.value,
    threshold_bpm: parseFloat(dom.ctrlThreshold.value),
    duration_s: parseFloat(dom.ctrlDuration.value),
    cache_size_bytes: parseInt(dom.ctrlCacheSize.value, 10),
    line_size_bytes: parseInt(dom.ctrlLineSize.value, 10),
    associativity: parseInt(dom.ctrlAssociativity.value, 10),
    active_fraction: activeFraction,
  };

  // Client-side quick range validations
  if (payload.threshold_bpm < 40 || payload.threshold_bpm > 220) {
    showErrorBanner("Threshold must be between 40 and 220 BPM (physiological limits).");
    return;
  }
  if (payload.duration_s < 1 || payload.duration_s > 60) {
    showErrorBanner("Duration must be between 1 and 60 seconds.");
    return;
  }

  // Set loading state
  dom.btnRunSim.disabled = true;
  dom.simSpinner.style.display = "inline-block";
  dom.btnRunText.textContent = "Simulating...";

  try {
    const data = await fetchJson("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    state.lastResult = data;
    hideErrorBanner();

    // Render all subsystems
    renderKPIs(data);
    renderWaveformChart(data);
    renderNumberRepresentation(data);
    renderALU(data);
    renderARMStepper(data, 0); // reset stepper to start
    renderCache(data);
    renderSerial(data);
    renderEnergy(data);

    // Placeholder alert banner check
    if (data.meta && data.meta.placeholders_in_use) {
      dom.placeholderBanner.style.display = "block";
    }

  } catch (err) {
    console.error("Simulation run failed:", err);
    let msg = "Simulation failed: ";
    if (err.status === 422 && err.detail) {
      if (Array.isArray(err.detail)) {
        msg = "Validation Error: " + err.detail.join("; ");
      } else {
        msg = "Validation Error: " + JSON.stringify(err.detail);
      }
    } else {
      msg += err.detail || err.message;
    }
    showErrorBanner(msg);
  } finally {
    dom.btnRunSim.disabled = false;
    dom.simSpinner.style.display = "none";
    dom.btnRunText.textContent = "▶ Run Simulation";
  }
}

// ============================================================================
// KPI Summary Cards Rendering
// ============================================================================

function renderKPIs(data) {
  // 1. Heart Rate & Alert
  const bpm = data.heart_rate.bpm;
  dom.kpiHrVal.innerHTML = `${Math.round(bpm)} <span class="kpi-unit">BPM</span>`;
  if (data.heart_rate.alert) {
    dom.kpiAlertBadge.textContent = "ALERT (TACHYCARDIA)";
    dom.kpiAlertBadge.className = "kpi-badge badge-alert";
  } else {
    dom.kpiAlertBadge.textContent = "NORMAL";
    dom.kpiAlertBadge.className = "kpi-badge badge-normal";
  }

  // 2. ALU Branch Decision & Flags
  const branchTaken = data.alu.branch_taken;
  dom.kpiBranchVal.textContent = branchTaken ? "BGT: YES (ALERT)" : "BGT: NO";
  if (branchTaken) {
    dom.kpiBranchVal.style.color = "var(--color-danger)";
  } else {
    dom.kpiBranchVal.style.color = "var(--color-success)";
  }

  const flags = data.alu.flags;
  setFlagChip(dom.chipFlagN, flags.N);
  setFlagChip(dom.chipFlagZ, flags.Z);
  setFlagChip(dom.chipFlagC, flags.C);
  setFlagChip(dom.chipFlagV, flags.V);

  // 3. Cache Performance & AMAT
  const hitRatePct = (data.cache.hit_rate * 100).toFixed(1);
  dom.kpiCacheVal.textContent = `${hitRatePct}%`;
  dom.kpiAmatVal.textContent = `AMAT: ${data.cache.amat_cycles.toFixed(2)} cyc`;

  // 4. Energy Current & Savings
  dom.kpiEnergyVal.innerHTML = `${data.energy.avg_current_ua.toFixed(1)} <span class="kpi-unit">&mu;A</span>`;
  dom.kpiSavingsBadge.textContent = `${data.energy.saving_pct.toFixed(1)}% Saved`;
}

function setFlagChip(elem, active) {
  if (active) {
    elem.classList.add("active");
  } else {
    elem.classList.remove("active");
  }
}

// ============================================================================
// Waveform Chart Controller (Chart.js)
// ============================================================================

function renderWaveformChart(data) {
  if (!window.Chart) {
    console.warn("Chart.js not loaded.");
    return;
  }

  const fs = data.meta.fs_hz || 125.0;
  const rawAdc = data.signal.raw_adc;
  const filteredQ15 = data.signal.filtered_q15;
  const peaks = new Set(data.signal.peaks);

  const totalPoints = rawAdc.length;
  // Subsample if duration > 20s to ensure buttery 60fps rendering
  const stride = totalPoints > 2500 ? Math.ceil(totalPoints / 1250) : 1;

  const timeLabels = [];
  const adcData = [];
  const filteredData = [];
  const peakPoints = [];

  for (let i = 0; i < totalPoints; i += stride) {
    const t = (i / fs).toFixed(3);
    timeLabels.push(t);
    adcData.push(rawAdc[i]);
    filteredData.push(filteredQ15[i]);

    // Check if any peak falls within this stride
    let hasPeak = false;
    for (let k = 0; k < stride && (i + k) < totalPoints; k++) {
      if (peaks.has(i + k)) {
        hasPeak = true;
        break;
      }
    }
    peakPoints.push(hasPeak ? filteredQ15[i] : null);
  }

  // Colors adapted for dark/light themes
  const isDark = state.theme === "dark";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.08)";
  const textColor = isDark ? "#a0aec0" : "#4a5568";

  if (state.chartInstance) {
    state.chartInstance.destroy();
  }

  const ctx = dom.waveformChart.getContext("2d");
  state.chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: timeLabels,
      datasets: [
        {
          label: "Raw 12-bit ADC [0, 4095]",
          data: adcData,
          yAxisID: "yADC",
          borderColor: isDark ? "rgba(160, 174, 192, 0.45)" : "rgba(113, 128, 150, 0.45)",
          borderWidth: 1,
          pointRadius: 0,
          borderDash: [3, 3],
          tension: 0.1,
          hidden: !dom.chkShowAdc.checked,
        },
        {
          label: "ARM Filtered Q15 [-32768, 32767]",
          data: filteredData,
          yAxisID: "yQ15",
          borderColor: "#319795",
          backgroundColor: isDark ? "rgba(49, 151, 149, 0.12)" : "rgba(49, 151, 149, 0.08)",
          borderWidth: 2,
          pointRadius: 0,
          fill: true,
          tension: 0.2,
          hidden: !dom.chkShowFiltered.checked,
        },
        {
          label: "Systolic Peaks (BPM)",
          data: peakPoints,
          yAxisID: "yQ15",
          type: "line",
          showLine: false,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: "#e53e3e",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 1.5,
          hidden: !dom.chkShowPeaks.checked,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => `Time: ${items[0].label}s`,
            label: (item) => {
              if (item.datasetIndex === 0) return ` Raw ADC: ${item.raw}`;
              if (item.datasetIndex === 1) return ` Filtered Q15: ${item.raw}`;
              if (item.datasetIndex === 2 && item.raw !== null) return ` ❤️ Systolic Peak Detected`;
              return "";
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "Time (seconds)", color: textColor },
          grid: { color: gridColor },
          ticks: { color: textColor, maxTicksLimit: 12 },
        },
        yQ15: {
          type: "linear",
          position: "left",
          title: { display: true, text: "Q15 Fixed-Point Amplitude", color: "#319795" },
          grid: { color: gridColor },
          ticks: { color: textColor },
        },
        yADC: {
          type: "linear",
          position: "right",
          title: { display: true, text: "Raw 12-bit ADC Integer", color: textColor },
          grid: { drawOnChartArea: false },
          ticks: { color: textColor },
          min: 0,
          max: 4095,
        },
      },
    },
  });
}

function updateChartDatasetVisibility() {
  if (!state.chartInstance) return;
  state.chartInstance.data.datasets[0].hidden = !dom.chkShowAdc.checked;
  state.chartInstance.data.datasets[1].hidden = !dom.chkShowFiltered.checked;
  state.chartInstance.data.datasets[2].hidden = !dom.chkShowPeaks.checked;
  state.chartInstance.update();
}

// ============================================================================
// Tab 1: Number Representation Rendering
// ============================================================================

function renderNumberRepresentation(data) {
  const last = data.number_repr.last_sample;
  dom.numLastAdc.textContent = last.adc;
  dom.numLastAdcHex.textContent = last.adc_hex;

  dom.numLastQ15.textContent = last.q15;
  dom.numLastQ15Hex.textContent = last.q15_hex;

  dom.numLastFiltered.textContent = last.filtered;
  dom.numLastFilteredHex.textContent = last.filtered_hex;
}

// ============================================================================
// Tab 2: ALU & Flags Rendering
// ============================================================================

function renderALU(data) {
  const flags = data.alu.flags;
  setLED(dom.ledFlagN, flags.N);
  setLED(dom.ledFlagZ, flags.Z);
  setLED(dom.ledFlagC, flags.C);
  setLED(dom.ledFlagV, flags.V);

  // Subtraction result
  const rawRes = data.alu.result;
  const signedRes = rawRes > 0x7FFFFFFF ? rawRes - 0x100000000 : rawRes;
  dom.aluResultVal.textContent = `${signedRes >= 0 ? "+" : ""}${signedRes}`;
  dom.aluResultHex.textContent = "0x" + (rawRes >>> 0).toString(16).toUpperCase().padStart(8, "0");

  // Condition evaluation
  const taken = data.alu.branch_taken;
  dom.aluBranchEval.textContent = taken ? "Condition TRUE -> BGT Alert Taken" : "Condition FALSE -> Normal (No Alert)";
  dom.aluBranchEval.style.color = taken ? "var(--color-danger)" : "var(--color-success)";
}

function setLED(elem, active) {
  if (active) {
    elem.classList.add("active");
  } else {
    elem.classList.remove("active");
  }
}

// ============================================================================
// Tab 3: ARM Core Instruction Stepper
// ============================================================================

function renderARMStepper(data, stepIndex = 0) {
  const arm = data.arm;
  if (!arm || !arm.steps || arm.steps.length === 0) return;

  const totalSteps = arm.steps.length;
  state.armStepIndex = Math.max(0, Math.min(stepIndex, totalSteps - 1));
  const currentStep = arm.steps[state.armStepIndex];
  const prevStep = state.armStepIndex > 0 ? arm.steps[state.armStepIndex - 1] : null;

  // Counter
  dom.stepCounterText.textContent = `Instruction ${state.armStepIndex + 1} of ${totalSteps}`;

  // Active opcode
  dom.activeInstrCode.textContent = currentStep.instruction;

  // Bit-exact verification badge
  if (arm.matches_python) {
    dom.armMatchBadge.textContent = "100% Bit-Exact Match with Python Reference";
    dom.armMatchBadge.className = "badge badge-success";
  } else {
    dom.armMatchBadge.textContent = "Mismatch with Python Reference";
    dom.armMatchBadge.className = "badge badge-alert";
  }

  // Register grid values and delta highlighting
  for (let i = 0; i < 8; i++) {
    const regName = `r${i}`;
    const val = currentStep.registers[regName] || 0;
    const hexStr = "0x" + (val >>> 0).toString(16).toUpperCase().padStart(8, "0");
    dom.regVals[regName].textContent = hexStr;

    // Highlight changed registers
    if (prevStep && prevStep.registers[regName] !== val) {
      dom.regBoxes[regName].classList.add("reg-changed");
    } else {
      dom.regBoxes[regName].classList.remove("reg-changed");
    }
  }

  // Button disabled states
  dom.btnStepFirst.disabled = state.armStepIndex === 0;
  dom.btnStepPrev.disabled = state.armStepIndex === 0;
  dom.btnStepNext.disabled = state.armStepIndex === totalSteps - 1;
  dom.btnStepLast.disabled = state.armStepIndex === totalSteps - 1;
}

function stepARMInstruction(action) {
  if (!state.lastResult || !state.lastResult.arm) return;
  const total = state.lastResult.arm.steps.length;

  if (action === "first") {
    state.armStepIndex = 0;
  } else if (action === "prev") {
    state.armStepIndex = Math.max(0, state.armStepIndex - 1);
  } else if (action === "next") {
    state.armStepIndex = Math.min(total - 1, state.armStepIndex + 1);
  } else if (action === "last") {
    state.armStepIndex = total - 1;
  }

  renderARMStepper(state.lastResult, state.armStepIndex);
}

// ============================================================================
// Tab 4: Cache Hierarchy Rendering
// ============================================================================

function renderCache(data) {
  const geom = data.cache.geometry;
  dom.bitTagCount.textContent = geom.tag_bits;
  dom.bitIndexCount.textContent = geom.index_bits;
  dom.bitOffsetCount.textContent = geom.offset_bits;

  // Dynamically size bit slices according to bit width
  dom.chunkTag.style.flex = `${geom.tag_bits} 1 0%`;
  dom.chunkIndex.style.flex = `${geom.index_bits} 1 0%`;
  dom.chunkOffset.style.flex = `${geom.offset_bits} 1 0%`;

  const hitRatePct = (data.cache.hit_rate * 100).toFixed(1);
  const missRatePct = (data.cache.miss_rate * 100).toFixed(1);

  dom.cacheHitrateVal.textContent = `${hitRatePct}%`;
  dom.cacheMissrateVal.textContent = `${missRatePct}%`;
  dom.cacheAmatVal.textContent = `${data.cache.amat_cycles.toFixed(2)} cyc`;
}

// ============================================================================
// Tab 5: Serial Interconnects Rendering
// ============================================================================

function renderSerial(data) {
  const u = data.serial.uart;
  dom.uartBaud.textContent = u.baud.toLocaleString();
  dom.uartMaxBps.textContent = u.bytes_per_s.toLocaleString();
  dom.uartUtil.textContent = `${u.utilisation_pct.toFixed(2)}%`;

  const i = data.serial.i2c;
  dom.i2cClock.textContent = (i.clock_hz / 1000).toString();
  dom.i2cLatency.textContent = i.transaction_us.toFixed(1);
  dom.i2cUtil.textContent = `${i.utilisation_pct.toFixed(2)}%`;
}

// ============================================================================
// Tab 6: Duty-Cycle Energy Rendering
// ============================================================================

function renderEnergy(data) {
  const e = data.energy;
  dom.energyTabAvg.innerHTML = `${e.avg_current_ua.toFixed(1)} <span class="data-unit">&mu;A</span>`;
  dom.energyTabBase.innerHTML = `${e.always_on_ua.toFixed(1)} <span class="data-unit">&mu;A</span>`;
  dom.energyTabSavings.textContent = `${e.saving_pct.toFixed(1)}%`;

  if (e.source) {
    const mcu = e.source.mcu || "STM32L476RG";
    const doc = e.source.datasheet_doc || "";
    const run = e.source.run_mode_table || "";
    const sleep = e.source.sleep_mode_table || "";
    dom.energySourceText.textContent = `${mcu}: ${doc} (${run}, ${sleep})`;
  }
}

// ============================================================================
// Tab 7: Verification Suite (GET /api/verification)
// ============================================================================

async function loadVerification() {
  try {
    const data = await fetchJson("/api/verification");
    state.verificationData = data;

    // 1. Q15 check
    const q15 = data.checks.q15_vs_float;
    dom.verifyQ15Mae.textContent = q15.max_absolute_error.toExponential(3);
    dom.verifyQ15Mean.textContent = q15.mean_absolute_error.toExponential(3);
    dom.verifyQ15Rmse.textContent = q15.rmse.toExponential(3);
    dom.verifyQ15Snr.textContent = `${q15.snr_db} dB`;
    setVerifyBadge(dom.badgeVerifyQ15, dom.iconVerifyQ15, q15.passed);

    // 2. ARM check
    const arm = data.checks.arm_vs_python;
    dom.verifyArmVectors.textContent = arm.vectors_tested;
    dom.verifyArmMismatches.textContent = arm.mismatches;
    setVerifyBadge(dom.badgeVerifyArm, dom.iconVerifyArm, arm.passed);

    // 3. Cache check
    const c = data.checks.cache_vs_hand_calc;
    dom.verifyCacheHits.textContent = `${c.actual_hits} / ${c.total_accesses}`;
    dom.verifyCacheHitrate.textContent = `${(c.hit_rate * 100).toFixed(1)}%`;
    dom.verifyCacheAmat.textContent = `${c.amat_cycles.toFixed(1)} cyc`;
    setVerifyBadge(dom.badgeVerifyCache, dom.iconVerifyCache, c.passed);

  } catch (err) {
    console.warn("Failed to load verification suite:", err);
  }
}

function setVerifyBadge(badgeElem, iconElem, passed) {
  if (passed) {
    badgeElem.textContent = "PASSED";
    badgeElem.className = "verify-status-badge badge-success";
    iconElem.textContent = "✅";
  } else {
    badgeElem.textContent = "FAILED";
    badgeElem.className = "verify-status-badge badge-alert";
    iconElem.textContent = "❌";
  }
}

// ============================================================================
// Tab 8: Traceability (GET /api/traceability)
// ============================================================================

async function loadTraceability() {
  try {
    const data = await fetchJson("/api/traceability");
    state.traceabilityData = data;

    // Render CO table
    dom.tbodyCoMapping.innerHTML = "";
    if (data.course_outcomes && data.course_outcomes.length > 0) {
      data.course_outcomes.forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${escapeHtml(row["CO"] || "")}</strong></td>
          <td>${renderSyllabusNotice(row["Official Syllabus Description"] || "")}</td>
          <td>${escapeHtml(row["COA Concept Demonstrated"] || "")}</td>
          <td><code>${escapeHtml(row["Module"] || "")}</code></td>
          <td><code>${escapeHtml(row["Test File"] || "")}</code></td>
        `;
        dom.tbodyCoMapping.appendChild(tr);
      });
    }

    // Render Dimension table
    dom.tbodyDimensionMapping.innerHTML = "";
    if (data.dimensions && data.dimensions.length > 0) {
      data.dimensions.forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${escapeHtml(row["Dimension"] || "")}</strong></td>
          <td>${renderSyllabusNotice(row["Full Name"] || "")}</td>
          <td>${renderSyllabusNotice(row["Official Rubric Description"] || "")}</td>
          <td>${escapeHtml(row["How Demonstrated in System"] || "")}</td>
        `;
        dom.tbodyDimensionMapping.appendChild(tr);
      });
    }

  } catch (err) {
    console.warn("Failed to load traceability mapping:", err);
  }
}

function renderSyllabusNotice(text) {
  if (!text || text.includes("To be confirmed from the syllabus")) {
    return `<span class="badge badge-unconfirmed">To be confirmed from the syllabus</span>`;
  }
  return escapeHtml(text);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ============================================================================
// Tab Navigation Controller
// ============================================================================

function switchTab(panelId) {
  dom.tabButtons.forEach((btn) => {
    const isTarget = btn.getAttribute("aria-controls") === panelId;
    btn.classList.toggle("active", isTarget);
    btn.setAttribute("aria-selected", isTarget ? "true" : "false");
  });

  dom.tabPanels.forEach((panel) => {
    panel.classList.toggle("active", panel.id === panelId);
  });
}

// ============================================================================
// "Start Here" Guided Tour (5 Steps)
// ============================================================================

const tourSteps = [
  {
    title: "1. Data Acquisition (Sensors & ADC)",
    body: `
      <p>The system acquires physiological Photoplethysmogram (PPG) pulses from optical sensors at 125 Hz.</p>
      <p>In this simulation, verified clinical data from the <strong>PhysioNet BIDMC Dataset</strong> or a deterministic <strong>Synthetic Generator</strong> models the analog sensor voltage digitized by a 12-bit ADC (range 0 to 4095).</p>
      <div class="tour-highlight">Key COA Concept: Sensor Interfacing &amp; ADC Digitization</div>
    `,
  },
  {
    title: "2. Number Representation (Signed Q15)",
    body: `
      <p>Embedded biomedical microcontrollers lack floating-point units (FPU) to conserve silicon and energy. Real-time arithmetic uses <strong>signed Q15 fixed-point format</strong>.</p>
      <p>The unsigned 12-bit ADC reading is converted with zero software division overhead: <code>(ADC &minus; 2048) &lt;&lt; 4</code>, mapping midscale to 0 and preserving precision.</p>
      <div class="tour-highlight">Key COA Concept: Fixed-Point Arithmetic &amp; Two's Complement (CO1)</div>
    `,
  },
  {
    title: "3. ARM Cortex-M Core & Thumb Instruction Filtering",
    body: `
      <p>A 4-sample boxcar moving average filter executes directly on the <strong>Unicorn ARM Emulator</strong> using genuine 16-bit Thumb machine code (<code>asm/moving_average.s</code>).</p>
      <p>The interactive instruction stepper lets you inspect low registers (R0&ndash;R7) and flags as halfwords are loaded, summed, and scaled by two's complement shifts (<code>ASRS #2</code>).</p>
      <div class="tour-highlight">Key COA Concept: Thumb Instruction Execution &amp; Register File (CO3)</div>
    `,
  },
  {
    title: "4. ALU Architecture & Alert Decision Branching",
    body: `
      <p>The 32-bit Arithmetic Logic Unit evaluates safety conditions using two's complement subtraction: <code>CMP bpm, threshold</code>.</p>
      <p>The four status flags in the <strong>Application Program Status Register (APSR)</strong> (Negative <code>N</code>, Zero <code>Z</code>, Carry <code>C</code>, Overflow <code>V</code>) drive conditional branch <code>BGT</code> (Branch if Greater Than: <code>Z==0 &amp;&amp; N==V</code>).</p>
      <div class="tour-highlight">Key COA Concept: 32-bit ALU Architecture &amp; Status Flags (CO2)</div>
    `,
  },
  {
    title: "5. Memory Hierarchy (Cache) & Energy Duty Cycling",
    body: `
      <p>Circular buffer accesses exhibit strong spatial and temporal locality, yielding &gt;90% cache hit rates and reducing Average Memory Access Time (AMAT) from 20 wait-state cycles to &lt;3 cycles.</p>
      <p>Between signal bursts, the processor halts oscillators and enters Stop 2 sleep mode. Duty-cycling active execution achieves <strong>&gt;90% energy savings</strong> over continuous operation.</p>
      <div class="tour-highlight">Key COA Concept: Cache Memory (CO4) &amp; Power-Aware Architecture (CO6)</div>
    `,
  },
];

function openTour() {
  state.tourCurrentStep = 0;
  renderTourStep();
  dom.tourModal.style.display = "flex";
}

function closeTour() {
  dom.tourModal.style.display = "none";
}

function renderTourStep() {
  const step = tourSteps[state.tourCurrentStep];
  dom.tourStepBadge.textContent = `Step ${state.tourCurrentStep + 1} of ${tourSteps.length}`;
  dom.tourStepTitle.textContent = step.title;
  dom.tourStepBody.innerHTML = step.body;

  dom.btnTourPrev.disabled = state.tourCurrentStep === 0;
  dom.btnTourNext.textContent = state.tourCurrentStep === tourSteps.length - 1 ? "Finish ✓" : "Next ▶";
}

function tourNext() {
  if (state.tourCurrentStep < tourSteps.length - 1) {
    state.tourCurrentStep++;
    renderTourStep();
  } else {
    closeTour();
  }
}

function tourPrev() {
  if (state.tourCurrentStep > 0) {
    state.tourCurrentStep--;
    renderTourStep();
  }
}

// ============================================================================
// Data Export Handlers (JSON & CSV)
// ============================================================================

function exportSimulationJson() {
  if (!state.lastResult) {
    showErrorBanner("No simulation run to export. Run the simulation first.");
    return;
  }
  const jsonStr = JSON.stringify(state.lastResult, null, 2);
  downloadBlob(jsonStr, "wearable_arm_simulation.json", "application/json");
}

function exportSignalCsv() {
  if (!state.lastResult || !state.lastResult.signal) {
    showErrorBanner("No signal data to export. Run the simulation first.");
    return;
  }

  const sig = state.lastResult.signal;
  const fs = state.lastResult.meta.fs_hz || 125.0;
  const peaksSet = new Set(sig.peaks);

  const rows = ["time_s,raw_adc,q15,filtered_q15,is_systolic_peak"];
  for (let i = 0; i < sig.raw_adc.length; i++) {
    const t = (i / fs).toFixed(4);
    const adc = sig.raw_adc[i];
    const q15 = sig.q15[i];
    const filt = sig.filtered_q15[i];
    const isPeak = peaksSet.has(i) ? 1 : 0;
    rows.push(`${t},${adc},${q15},${filt},${isPeak}`);
  }

  const csvStr = rows.join("\n");
  downloadBlob(csvStr, "physiological_ppg_signal.csv", "text/csv;charset=utf-8;");
}

function downloadBlob(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ============================================================================
// Theme Management (Dark / Light Mode)
// ============================================================================

function setupTheme() {
  const saved = localStorage.getItem("theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved ? saved : (prefersDark ? "dark" : "light");
  applyTheme(theme);
}

function toggleTheme() {
  const nextTheme = state.theme === "dark" ? "light" : "dark";
  applyTheme(nextTheme);
  localStorage.setItem("theme", nextTheme);
}

function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  dom.themeToggle.textContent = theme === "dark" ? "🌙" : "☀️";

  // Re-render chart if it exists to adapt gridlines & axes
  if (state.lastResult && state.chartInstance) {
    renderWaveformChart(state.lastResult);
  }
}

// ============================================================================
// App Bootstrap
// ============================================================================

document.addEventListener("DOMContentLoaded", initializeApp);
