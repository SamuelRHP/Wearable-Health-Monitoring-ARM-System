/**
 * Wearable Health-Monitoring ARM System - Frontend Application
 *
 * Microarchitectural physiological signal monitoring dashboard demonstrating
 * COA concepts: Number representation (Q15), ALU flags, Thumb assembly,
 * SRAM cache hierarchy, UART/I2C serial bus, and duty-cycled energy.
 *
 * Supports independent Demo View (presenter-friendly) and Details View.
 */

"use strict";

// ============================================================================
// State Management
// ============================================================================

const state = {
  backendOnline: false,
  defaults: null,
  demoResult: null,
  detailsResult: null,
  lastResult: null, // alias for export
  demoChartInstance: null,
  detailsChartInstance: null,
  chartInstance: null,
  armStepIndex: 0,
  tourCurrentStep: 0,
  verificationData: null,
  theme: "light", // default light theme
  currentView: "demo", // "demo" or "details"
};

// ============================================================================
// DOM Element Selectors
// ============================================================================

const dom = {
  // Header & Status
  backendStatus: document.getElementById("backend-status"),
  backendStatusText: document.getElementById("backend-status-text"),
  btnViewDemo: document.getElementById("btn-view-demo"),
  btnViewDetails: document.getElementById("btn-view-details"),
  btnBackToDemo: document.getElementById("btn-back-to-demo"),
  panelDemo: document.getElementById("panel-demo"),
  panelDetails: document.getElementById("panel-details"),
  btnExportJson: document.getElementById("btn-export-json"),
  btnExportCsv: document.getElementById("btn-export-csv"),
  menuBtnTour: document.getElementById("menu-btn-tour"),
  themeToggle: document.getElementById("theme-toggle"),

  // Banners & Notifications
  placeholderBanner: document.getElementById("placeholder-banner"),
  placeholderBannerText: document.getElementById("placeholder-banner-text"),
  globalErrorBanner: document.getElementById("global-error-banner"),
  globalErrorText: document.getElementById("global-error-text"),
  btnCloseError: document.getElementById("btn-close-error"),

  // Demo Controls & Presets
  demoThreshold: document.getElementById("demo-threshold"),
  demoThresholdNum: document.getElementById("demo-threshold-num"),
  demoActiveFrac: document.getElementById("demo-active-frac"),
  demoActiveFracNum: document.getElementById("demo-active-frac-num"),
  demoCacheSize: document.getElementById("demo-cache-size"),
  btnDemoRun: document.getElementById("btn-demo-run"),
  btnDemoReset: document.getElementById("btn-demo-reset"),
  demoSimSpinner: document.getElementById("demo-sim-spinner"),
  btnDemoRunText: document.getElementById("btn-demo-run-text"),
  btnPresetNormal: document.getElementById("btn-preset-normal"),
  btnPresetAlert: document.getElementById("btn-preset-alert"),

  // Horizontal Pipeline Strip Elements
  pipeValQ15: document.getElementById("pipe-val-q15"),
  pipeValArm: document.getElementById("pipe-val-arm"),
  pipeValAlu: document.getElementById("pipe-val-alu"),
  pipeFlagsText: document.getElementById("pipe-flags-text"),
  pipeBranchText: document.getElementById("pipe-branch-text"),
  pipeValCache: document.getElementById("pipe-val-cache"),
  pipeValSerial: document.getElementById("pipe-val-serial"),
  pipeValEnergy: document.getElementById("pipe-val-energy"),
  pipelineSteps: document.querySelectorAll(".pipeline-step"),

  // Details Form Controls
  ctrlSource: document.getElementById("ctrl-source"),
  grpTargetBpm: document.getElementById("grp-target-bpm"),
  ctrlTargetBpm: document.getElementById("ctrl-target-bpm"),
  ctrlTargetBpmNum: document.getElementById("ctrl-target-bpm-num"),
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

  // Summary KPI Cards (Demo View)
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
  demoEnergyPlaceholderChip: document.getElementById("demo-energy-placeholder-chip"),

  // Summary KPI Cards (Details View)
  detailsKpiHrVal: document.getElementById("details-kpi-hr-val"),
  detailsKpiAlertBadge: document.getElementById("details-kpi-alert-badge"),
  detailsKpiBranchVal: document.getElementById("details-kpi-branch-val"),
  detailsChipFlagN: document.getElementById("details-chip-flag-n"),
  detailsChipFlagZ: document.getElementById("details-chip-flag-z"),
  detailsChipFlagC: document.getElementById("details-chip-flag-c"),
  detailsChipFlagV: document.getElementById("details-chip-flag-v"),
  detailsKpiCacheVal: document.getElementById("details-kpi-cache-val"),
  detailsKpiAmatVal: document.getElementById("details-kpi-amat-val"),
  detailsKpiEnergyVal: document.getElementById("details-kpi-energy-val"),
  detailsKpiSavingsBadge: document.getElementById("details-kpi-savings-badge"),
  detailsEnergyPlaceholderChip: document.getElementById("details-energy-placeholder-chip"),

  // Chart Canvas & Toggles (Demo & Details)
  waveformChart: document.getElementById("waveform-chart"),
  chkShowAdc: document.getElementById("chk-show-adc"),
  chkShowFiltered: document.getElementById("chk-show-filtered"),
  chkShowPeaks: document.getElementById("chk-show-peaks"),
  detailsWaveformChart: document.getElementById("details-waveform-chart"),
  chkDetailsShowAdc: document.getElementById("chk-details-show-adc"),
  chkDetailsShowFiltered: document.getElementById("chk-details-show-filtered"),
  chkDetailsShowPeaks: document.getElementById("chk-details-show-peaks"),

  // Tabs Navigation & Panels (Details View)
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
  armStepSummary: document.getElementById("arm-step-summary"),
  armStepTableBody: document.getElementById("arm-step-table-body"),
  btnStepFirst: document.getElementById("btn-step-first"),
  btnStepPrev: document.getElementById("btn-step-prev"),
  btnStepNext: document.getElementById("btn-step-next"),
  btnStepLast: document.getElementById("btn-step-last"),
  stepCounterText: document.getElementById("step-counter-text"),
  armVerificationStatus: document.getElementById("arm-verification-status"),

  // Tab 4: Cache
  cacheLinesTotal: document.getElementById("cache-lines-total"),
  cacheOffsetBits: document.getElementById("cache-offset-bits"),
  cacheIndexBits: document.getElementById("cache-index-bits"),
  cacheTagBits: document.getElementById("cache-tag-bits"),
  cacheTotalHits: document.getElementById("cache-total-hits"),
  cacheTotalMisses: document.getElementById("cache-total-misses"),
  cacheHitRatePct: document.getElementById("cache-hitrate-pct"),
  cacheAmatValue: document.getElementById("cache-amat-value"),
  cacheBarHit: document.getElementById("cache-bar-hit"),
  cacheBarMiss: document.getElementById("cache-bar-miss"),

  // Tab 5: Serial I/O
  uartBaudRate: document.getElementById("uart-baud-rate"),
  uartByteRate: document.getElementById("uart-byte-rate"),
  uartUtilPct: document.getElementById("uart-util-pct"),
  uartPacketHex: document.getElementById("uart-packet-hex"),
  i2cClkFreq: document.getElementById("i2c-clk-freq"),
  i2cByteRate: document.getElementById("i2c-byte-rate"),
  i2cDutyPct: document.getElementById("i2c-duty-pct"),

  // Tab 6: Energy
  energyActiveCurrent: document.getElementById("energy-active-current"),
  energySleepCurrent: document.getElementById("energy-sleep-current"),
  energyAvgCurrent: document.getElementById("energy-avg-current"),
  energyBaselineCurrent: document.getElementById("energy-baseline-current"),
  energySavingPct: document.getElementById("energy-saving-pct"),
  energySourceText: document.getElementById("energy-source-text"),

  // Tab 7: Verification Suite
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

  // Guided Tour Modal
  tourModal: document.getElementById("tour-modal"),
  tourStepTitle: document.getElementById("tour-step-title"),
  tourStepIndicator: document.getElementById("tour-step-indicator"),
  tourStepBody: document.getElementById("tour-step-body"),
  btnTourClose: document.getElementById("btn-tour-close"),
  btnTourPrev: document.getElementById("btn-tour-prev"),
  btnTourNext: document.getElementById("btn-tour-next"),
};

// ============================================================================
// API & Communication Layer
// ============================================================================

async function fetchJson(endpoint, options = {}) {
  const resp = await fetch(endpoint, options);
  if (!resp.ok) {
    let errorDetail = `HTTP ${resp.status} ${resp.statusText}`;
    try {
      const errJson = await resp.json();
      if (errJson && errJson.detail) {
        if (Array.isArray(errJson.detail)) {
          errorDetail = errJson.detail.map((d) => `${d.loc ? d.loc.join(".") : ""}: ${d.msg}`).join("; ");
        } else {
          errorDetail = String(errJson.detail);
        }
      }
    } catch (_) {
      // Non-JSON response
    }
    throw new Error(errorDetail);
  }
  return await resp.json();
}

async function checkHealth() {
  try {
    const health = await fetchJson("/api/health");
    if (health && health.status === "ok") {
      setBackendStatus(true);
      return true;
    }
    setBackendStatus(false);
    return false;
  } catch (err) {
    setBackendStatus(false);
    return false;
  }
}

function setBackendStatus(online) {
  state.backendOnline = online;
  if (online) {
    dom.backendStatus.className = "status-chip status-online";
    dom.backendStatusText.textContent = "Backend Connected";
  } else {
    dom.backendStatus.className = "status-chip status-offline";
    dom.backendStatusText.textContent = "Backend Offline (Port 8000)";
  }
}

function showErrorBanner(message) {
  dom.globalErrorText.textContent = message;
  dom.globalErrorBanner.style.display = "flex";
}

function hideErrorBanner() {
  dom.globalErrorBanner.style.display = "none";
}

// ============================================================================
// View Switcher & Tab Navigation
// ============================================================================

function switchView(viewName) {
  state.currentView = viewName;
  if (viewName === "demo") {
    dom.panelDemo.style.display = "flex";
    dom.panelDemo.classList.add("active");
    dom.panelDetails.style.display = "none";
    dom.panelDetails.classList.remove("active");

    dom.btnViewDemo.classList.add("active");
    dom.btnViewDemo.setAttribute("aria-pressed", "true");
    dom.btnViewDetails.classList.remove("active");
    dom.btnViewDetails.setAttribute("aria-pressed", "false");

    // Re-render chart for Demo view
    if (state.demoResult) {
      setTimeout(() => {
        renderDemoWaveformChart(state.demoResult);
      }, 50);
    }
  } else if (viewName === "details") {
    dom.panelDemo.style.display = "none";
    dom.panelDemo.classList.remove("active");
    dom.panelDetails.style.display = "block";
    dom.panelDetails.classList.add("active");

    dom.btnViewDemo.classList.remove("active");
    dom.btnViewDemo.setAttribute("aria-pressed", "false");
    dom.btnViewDetails.classList.add("active");
    dom.btnViewDetails.setAttribute("aria-pressed", "true");

    // Re-render chart for Details view
    if (state.detailsResult) {
      setTimeout(() => {
        renderDetailsWaveformChart(state.detailsResult);
      }, 50);
    }
  }
}

function openDetailsTab(tabId) {
  switchView("details");
  switchTab(tabId);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function switchTab(tabId) {
  dom.tabButtons.forEach((btn) => {
    const isTarget = btn.getAttribute("aria-controls") === tabId;
    btn.classList.toggle("active", isTarget);
    btn.setAttribute("aria-selected", isTarget ? "true" : "false");
  });

  dom.tabPanels.forEach((panel) => {
    const isTarget = panel.id === tabId;
    panel.classList.toggle("active", isTarget);
  });
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
    await runDemoSimulation();
    await runDetailsSimulation();
    await loadVerification();
  } else {
    showErrorBanner("Cannot connect to FastAPI backend at http://localhost:8000. Start it in terminal with: python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload");
  }

  // Periodic health check every 10 seconds
  setInterval(async () => {
    const wasOnline = state.backendOnline;
    const nowOnline = await checkHealth();
    if (!wasOnline && nowOnline) {
      hideErrorBanner();
      if (!state.demoResult) {
        await runDemoSimulation();
      }
      if (!state.detailsResult) {
        await runDetailsSimulation();
      }
    }
  }, 10000);
}

async function loadDefaultsAndSync() {
  try {
    const config = await fetchJson("/api/defaults");
    state.defaults = config;

    const d = config.defaults;
    if (d) {
      // Set Details view controls
      dom.ctrlSource.value = d.source || "synthetic";
      if (dom.ctrlTargetBpm) {
        dom.ctrlTargetBpm.value = d.target_bpm || 75;
        dom.ctrlTargetBpmNum.value = d.target_bpm || 75;
      }
      if (dom.grpTargetBpm) {
        dom.grpTargetBpm.style.display = (dom.ctrlSource.value === "synthetic") ? "block" : "none";
      }
      dom.ctrlThreshold.value = d.threshold_bpm || 100;
      dom.ctrlThresholdNum.value = d.threshold_bpm || 100;
      dom.ctrlDuration.value = d.duration_s || 10;
      dom.ctrlDurationNum.value = d.duration_s || 10;
      dom.ctrlCacheSize.value = d.cache_size_bytes || 4096;
      dom.ctrlLineSize.value = d.line_size_bytes || 16;
      dom.ctrlAssociativity.value = d.associativity || 1;
      const actFrac = (d.active_fraction !== undefined ? d.active_fraction * 100.0 : 5.0).toFixed(1);
      dom.ctrlActiveFrac.value = actFrac;
      dom.ctrlActiveFracNum.value = actFrac;

      // Set Demo view controls independently
      dom.demoThreshold.value = d.threshold_bpm || 100;
      dom.demoThresholdNum.value = d.threshold_bpm || 100;
      dom.demoActiveFrac.value = actFrac;
      dom.demoActiveFracNum.value = actFrac;
      dom.demoCacheSize.value = d.cache_size_bytes || 4096;
    }
  } catch (err) {
    console.warn("Could not load /api/defaults, using hardcoded defaults:", err);
  }
}

function resetDemoDefaults() {
  if (state.defaults && state.defaults.defaults) {
    const d = state.defaults.defaults;
    const actFrac = (d.active_fraction !== undefined ? d.active_fraction * 100.0 : 5.0).toFixed(1);
    dom.demoThreshold.value = d.threshold_bpm || 100;
    dom.demoThresholdNum.value = d.threshold_bpm || 100;
    dom.demoActiveFrac.value = actFrac;
    dom.demoActiveFracNum.value = actFrac;
    dom.demoCacheSize.value = d.cache_size_bytes || 4096;
  }
}

function resetDetailsDefaults() {
  if (state.defaults && state.defaults.defaults) {
    const d = state.defaults.defaults;
    dom.ctrlSource.value = d.source || "synthetic";
    if (dom.ctrlTargetBpm) {
      dom.ctrlTargetBpm.value = d.target_bpm || 75;
      dom.ctrlTargetBpmNum.value = d.target_bpm || 75;
    }
    if (dom.grpTargetBpm) {
      dom.grpTargetBpm.style.display = (dom.ctrlSource.value === "synthetic") ? "block" : "none";
    }
    dom.ctrlThreshold.value = d.threshold_bpm || 100;
    dom.ctrlThresholdNum.value = d.threshold_bpm || 100;
    dom.ctrlDuration.value = d.duration_s || 10;
    dom.ctrlDurationNum.value = d.duration_s || 10;
    dom.ctrlCacheSize.value = d.cache_size_bytes || 4096;
    dom.ctrlLineSize.value = d.line_size_bytes || 16;
    dom.ctrlAssociativity.value = d.associativity || 1;
    const actFrac = (d.active_fraction !== undefined ? d.active_fraction * 100.0 : 5.0).toFixed(1);
    dom.ctrlActiveFrac.value = actFrac;
    dom.ctrlActiveFracNum.value = actFrac;
  }
}

// ============================================================================
// 1-Click Quick Presets (Demo View Only)
// ============================================================================

async function applyPreset(type) {
  if (type === "normal") {
    // Normal preset: 75 bpm, threshold 100
    if (dom.demoThreshold) dom.demoThreshold.value = 100;
    if (dom.demoThresholdNum) dom.demoThresholdNum.value = 100;
    if (dom.demoActiveFrac) dom.demoActiveFrac.value = "5.0";
    if (dom.demoActiveFracNum) dom.demoActiveFracNum.value = "5.0";
    if (dom.demoCacheSize) dom.demoCacheSize.value = 4096;
    await runDemoSimulation();
  } else if (type === "alert") {
    // Trigger alert preset: threshold 70
    if (dom.demoThreshold) dom.demoThreshold.value = 70;
    if (dom.demoThresholdNum) dom.demoThresholdNum.value = 70;
    if (dom.demoActiveFrac) dom.demoActiveFrac.value = "5.0";
    if (dom.demoActiveFracNum) dom.demoActiveFracNum.value = "5.0";
    if (dom.demoCacheSize) dom.demoCacheSize.value = 4096;
    await runDemoSimulation();
  }
}

// ============================================================================
// Form Event Handlers & Sliders
// ============================================================================

function setupSliders() {
  function bindPair(slider, num) {
    if (!slider || !num) return;
    slider.addEventListener("input", () => {
      num.value = slider.value;
    });
    num.addEventListener("input", () => {
      const val = parseFloat(num.value);
      if (!isNaN(val)) {
        slider.value = val;
      }
    });
  }

  // Demo controls (independent)
  bindPair(dom.demoThreshold, dom.demoThresholdNum);
  bindPair(dom.demoActiveFrac, dom.demoActiveFracNum);

  // Details controls (independent)
  bindPair(dom.ctrlThreshold, dom.ctrlThresholdNum);
  bindPair(dom.ctrlActiveFrac, dom.ctrlActiveFracNum);
  bindPair(dom.ctrlTargetBpm, dom.ctrlTargetBpmNum);
  bindPair(dom.ctrlDuration, dom.ctrlDurationNum);

  // Toggle Simulated Heart Rate based on source
  if (dom.ctrlSource && dom.grpTargetBpm) {
    dom.ctrlSource.addEventListener("change", () => {
      dom.grpTargetBpm.style.display = (dom.ctrlSource.value === "synthetic") ? "block" : "none";
    });
  }
}

function setupEventListeners() {
  // View switcher buttons
  dom.btnViewDemo.addEventListener("click", () => switchView("demo"));
  dom.btnViewDetails.addEventListener("click", () => switchView("details"));
  dom.btnBackToDemo.addEventListener("click", () => switchView("demo"));

  // Pipeline step clicks and any data-tab shortcuts jump to corresponding concept tab in Details
  document.querySelectorAll("[data-tab]").forEach((item) => {
    item.addEventListener("click", () => {
      const tabId = item.getAttribute("data-tab");
      if (tabId) openDetailsTab(tabId);
    });
  });

  // 1-Click quick presets (Demo view)
  dom.btnPresetNormal.addEventListener("click", () => applyPreset("normal"));
  dom.btnPresetAlert.addEventListener("click", () => applyPreset("alert"));

  // Demo Simulation run and reset buttons
  dom.btnDemoRun.addEventListener("click", () => runDemoSimulation());
  dom.btnDemoReset.addEventListener("click", async () => {
    resetDemoDefaults();
    await runDemoSimulation();
  });

  // Details Simulation run and reset buttons
  dom.btnRunSim.addEventListener("click", () => runDetailsSimulation());
  dom.btnResetDefaults.addEventListener("click", async () => {
    resetDetailsDefaults();
    await runDetailsSimulation();
  });

  // Pipeline step clicks jump to corresponding concept tab in Details
  dom.pipelineSteps.forEach((step) => {
    step.addEventListener("click", () => {
      const targetTab = step.getAttribute("data-tab");
      if (targetTab) openDetailsTab(targetTab);
    });
  });

  // Close global error alert
  dom.btnCloseError.addEventListener("click", () => hideErrorBanner());

  // Chart toggles (Demo View)
  dom.chkShowAdc.addEventListener("change", () => updateChartDatasetVisibility(true));
  dom.chkShowFiltered.addEventListener("change", () => updateChartDatasetVisibility(true));
  dom.chkShowPeaks.addEventListener("change", () => updateChartDatasetVisibility(true));

  // Chart toggles (Details View)
  if (dom.chkDetailsShowAdc) {
    dom.chkDetailsShowAdc.addEventListener("change", () => updateChartDatasetVisibility(false));
  }
  if (dom.chkDetailsShowFiltered) {
    dom.chkDetailsShowFiltered.addEventListener("change", () => updateChartDatasetVisibility(false));
  }
  if (dom.chkDetailsShowPeaks) {
    dom.chkDetailsShowPeaks.addEventListener("change", () => updateChartDatasetVisibility(false));
  }

  // Tab switching in Details view
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
  if (dom.menuBtnTour) dom.menuBtnTour.addEventListener("click", () => openTour());
  dom.btnTourClose.addEventListener("click", () => closeTour());
  dom.btnTourNext.addEventListener("click", () => tourNext());
  dom.btnTourPrev.addEventListener("click", () => tourPrev());

  // Export actions
  dom.btnExportJson.addEventListener("click", () => exportSimulationJson());
  dom.btnExportCsv.addEventListener("click", () => exportSignalCsv());

  // Theme Toggle
  dom.themeToggle.addEventListener("click", () => toggleTheme());
}

// ============================================================================
// Simulation Execution (POST /api/run)
// ============================================================================

async function runDemoSimulation() {
  const activePercent = parseFloat(dom.demoActiveFrac.value || "5.0");
  const activeFraction = activePercent / 100.0;

  const payload = {
    source: "synthetic",
    threshold_bpm: parseFloat(dom.demoThreshold.value || "100"),
    duration_s: 10.0,
    target_bpm: 75.0,
    cache_size_bytes: parseInt(dom.demoCacheSize.value || "4096", 10),
    line_size_bytes: 16,
    associativity: 1,
    active_fraction: activeFraction,
  };

  if (payload.threshold_bpm < 40 || payload.threshold_bpm > 220) {
    showErrorBanner("Demo Threshold must be between 40 and 220 BPM.");
    return;
  }

  setDemoLoading(true);

  try {
    const data = await fetchJson("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    state.demoResult = data;
    state.lastResult = data;
    hideErrorBanner();

    // Render ONLY Demo elements
    renderDemoKPIs(data);
    renderPipelineStrip(data);
    renderDemoWaveformChart(data);

  } catch (err) {
    console.error("Demo simulation execution error:", err);
    showErrorBanner(`Demo simulation failed: ${err.message}`);
  } finally {
    setDemoLoading(false);
  }
}

async function runDetailsSimulation() {
  const activePercent = parseFloat(dom.ctrlActiveFrac.value || "5.0");
  const activeFraction = activePercent / 100.0;

  const payload = {
    source: dom.ctrlSource.value || "synthetic",
    threshold_bpm: parseFloat(dom.ctrlThreshold.value || "100"),
    duration_s: parseFloat(dom.ctrlDuration.value || "10.0"),
    target_bpm: parseFloat(dom.ctrlTargetBpm ? dom.ctrlTargetBpm.value : "75.0"),
    cache_size_bytes: parseInt(dom.ctrlCacheSize.value || "4096", 10),
    line_size_bytes: parseInt(dom.ctrlLineSize.value || "16", 10),
    associativity: parseInt(dom.ctrlAssociativity.value || "1", 10),
    active_fraction: activeFraction,
  };

  if (payload.threshold_bpm < 40 || payload.threshold_bpm > 220) {
    showErrorBanner("Threshold must be between 40 and 220 BPM (physiological limits).");
    return;
  }
  if (payload.duration_s < 1 || payload.duration_s > 60) {
    showErrorBanner("Duration must be between 1 and 60 seconds.");
    return;
  }

  setDetailsLoading(true);

  try {
    const data = await fetchJson("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    state.detailsResult = data;
    hideErrorBanner();

    // Render Details elements
    renderDetailsKPIs(data);
    renderDetailsWaveformChart(data);
    renderNumberRepresentation(data);
    renderAluFlags(data);
    renderArmCore(data);
    renderCache(data);
    renderSerial(data);
    renderEnergy(data);

    // Hard constraint 1: Show placeholder banner if energy placeholder flag is true
    if (data.energy && data.energy.placeholder) {
      dom.placeholderBanner.style.display = "block";
    } else {
      dom.placeholderBanner.style.display = "none";
    }

  } catch (err) {
    console.error("Details simulation execution error:", err);
    showErrorBanner(`Details simulation failed: ${err.message}`);
  } finally {
    setDetailsLoading(false);
  }
}

function setDemoLoading(isLoading) {
  if (dom.btnDemoRun) dom.btnDemoRun.disabled = isLoading;
  if (dom.btnPresetNormal) dom.btnPresetNormal.disabled = isLoading;
  if (dom.btnPresetAlert) dom.btnPresetAlert.disabled = isLoading;
  if (dom.btnDemoReset) dom.btnDemoReset.disabled = isLoading;

  if (dom.demoSimSpinner) dom.demoSimSpinner.style.display = isLoading ? "inline-block" : "none";

  const playSvg = '<svg class="icon" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg> Run Simulation';
  if (dom.btnDemoRunText) {
    dom.btnDemoRunText.innerHTML = isLoading ? "Simulating..." : playSvg;
  }
}

function setDetailsLoading(isLoading) {
  if (dom.btnRunSim) dom.btnRunSim.disabled = isLoading;
  if (dom.btnResetDefaults) dom.btnResetDefaults.disabled = isLoading;

  if (dom.simSpinner) dom.simSpinner.style.display = isLoading ? "inline-block" : "none";

  const playSvg = '<svg class="icon" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg> Run Simulation';
  if (dom.btnRunText) {
    dom.btnRunText.innerHTML = isLoading ? "Simulating..." : playSvg;
  }
}

// Backward compatibility alias
function runSimulation() {
  if (state.currentView === "demo") {
    return runDemoSimulation();
  } else {
    return runDetailsSimulation();
  }
}

// ============================================================================
// Horizontal Pipeline Strip Rendering
// ============================================================================

function renderPipelineStrip(data) {
  if (!data) return;

  // Step 1: ADC -> Q15
  const rawSample = data.signal.raw_adc[0] || 0;
  const q15Sample = data.signal.filtered_q15[0] || 0;
  if (dom.pipeValQ15) {
    dom.pipeValQ15.textContent = `0x${q15Sample >= 0 ? q15Sample.toString(16).toUpperCase() : (q15Sample & 0xffff).toString(16).toUpperCase()} (ADC ${rawSample})`;
  }

  // Step 2: ARM Boxcar Moving Average
  if (dom.pipeValArm) {
    dom.pipeValArm.textContent = `${data.arm.instruction_count} Thumb-2 Insns`;
  }

  // Step 3: ALU Compare & Status Flags
  const branchTaken = data.alu.branch_taken;
  const flags = data.alu.flags;
  const flagStr = `N:${flags.N ? 1 : 0} Z:${flags.Z ? 1 : 0} C:${flags.C ? 1 : 0} V:${flags.V ? 1 : 0}`;
  if (dom.pipeValAlu) {
    dom.pipeValAlu.textContent = branchTaken ? "BGT: Alert Active" : "BGT: Normal";
  }
  if (dom.pipeFlagsText) dom.pipeFlagsText.textContent = `Flags [${flagStr}]`;
  if (dom.pipeBranchText) dom.pipeBranchText.textContent = branchTaken ? "Branch: TAKEN" : "Branch: NOT TAKEN";

  // Step 4: SRAM Cache Hierarchy
  if (dom.pipeValCache) {
    dom.pipeValCache.textContent = `${(data.cache.hit_rate * 100).toFixed(1)}% Hit (${data.cache.amat_cycles.toFixed(1)} cyc)`;
  }

  // Step 5: Serial Bus I/O
  if (dom.pipeValSerial) {
    dom.pipeValSerial.textContent = `UART: ${(data.serial.uart.bus_utilization_pct).toFixed(1)}% | I2C: ${(data.serial.i2c.bus_duty_cycle_pct).toFixed(1)}%`;
  }

  // Step 6: Duty-Cycle Energy
  if (dom.pipeValEnergy) {
    dom.pipeValEnergy.textContent = `${data.energy.avg_current_ua.toFixed(1)} µA (${data.energy.saving_pct.toFixed(1)}% Saved)`;
  }
}

// ============================================================================
// KPI Cards Rendering (Demo View & Details View)
// ============================================================================

function renderDemoKPIs(data) {
  if (!data) return;
  // 1. Heart Rate & Alert
  const bpm = data.heart_rate.bpm;
  if (dom.kpiHrVal) dom.kpiHrVal.innerHTML = `${Math.round(bpm)} <span class="kpi-unit">BPM</span>`;
  if (dom.kpiAlertBadge) {
    if (data.heart_rate.alert) {
      dom.kpiAlertBadge.textContent = "ALERT (TACHYCARDIA)";
      dom.kpiAlertBadge.className = "kpi-badge badge-alert";
    } else {
      dom.kpiAlertBadge.textContent = "NORMAL";
      dom.kpiAlertBadge.className = "kpi-badge badge-normal";
    }
  }

  // 2. ALU Branch Decision & Flags
  const branchTaken = data.alu.branch_taken;
  if (dom.kpiBranchVal) {
    dom.kpiBranchVal.textContent = branchTaken ? "BGT: YES (ALERT)" : "BGT: NO";
    dom.kpiBranchVal.style.color = branchTaken ? "var(--accent-red)" : "var(--accent-green)";
  }

  const flags = data.alu.flags;
  setFlagChip(dom.chipFlagN, flags.N);
  setFlagChip(dom.chipFlagZ, flags.Z);
  setFlagChip(dom.chipFlagC, flags.C);
  setFlagChip(dom.chipFlagV, flags.V);

  // 3. Cache Performance & AMAT
  const hitRatePct = (data.cache.hit_rate * 100).toFixed(1);
  if (dom.kpiCacheVal) dom.kpiCacheVal.textContent = `${hitRatePct}%`;
  if (dom.kpiAmatVal) dom.kpiAmatVal.textContent = `AMAT: ${data.cache.amat_cycles.toFixed(2)} cyc`;

  // 4. Energy Current & Savings
  if (dom.kpiEnergyVal) dom.kpiEnergyVal.innerHTML = `${data.energy.avg_current_ua.toFixed(1)} <span class="kpi-unit">&mu;A</span>`;
  if (dom.kpiSavingsBadge) dom.kpiSavingsBadge.textContent = `${data.energy.saving_pct.toFixed(1)}% Saved`;
}

function renderDetailsKPIs(data) {
  if (!data) return;
  // 1. Heart Rate & Alert
  const bpm = data.heart_rate.bpm;
  if (dom.detailsKpiHrVal) dom.detailsKpiHrVal.innerHTML = `${Math.round(bpm)} <span class="kpi-unit">BPM</span>`;
  if (dom.detailsKpiAlertBadge) {
    if (data.heart_rate.alert) {
      dom.detailsKpiAlertBadge.textContent = "ALERT (TACHYCARDIA)";
      dom.detailsKpiAlertBadge.className = "kpi-badge badge-alert";
    } else {
      dom.detailsKpiAlertBadge.textContent = "NORMAL";
      dom.detailsKpiAlertBadge.className = "kpi-badge badge-normal";
    }
  }

  // 2. ALU Branch Decision & Flags
  const branchTaken = data.alu.branch_taken;
  if (dom.detailsKpiBranchVal) {
    dom.detailsKpiBranchVal.textContent = branchTaken ? "BGT: YES (ALERT)" : "BGT: NO";
    dom.detailsKpiBranchVal.style.color = branchTaken ? "var(--accent-red)" : "var(--accent-green)";
  }

  const flags = data.alu.flags;
  setFlagChip(dom.detailsChipFlagN, flags.N);
  setFlagChip(dom.detailsChipFlagZ, flags.Z);
  setFlagChip(dom.detailsChipFlagC, flags.C);
  setFlagChip(dom.detailsChipFlagV, flags.V);

  // 3. Cache Performance & AMAT
  const hitRatePct = (data.cache.hit_rate * 100).toFixed(1);
  if (dom.detailsKpiCacheVal) dom.detailsKpiCacheVal.textContent = `${hitRatePct}%`;
  if (dom.detailsKpiAmatVal) dom.detailsKpiAmatVal.textContent = `AMAT: ${data.cache.amat_cycles.toFixed(2)} cyc`;

  // 4. Energy Current & Savings
  if (dom.detailsKpiEnergyVal) dom.detailsKpiEnergyVal.innerHTML = `${data.energy.avg_current_ua.toFixed(1)} <span class="kpi-unit">&mu;A</span>`;
  if (dom.detailsKpiSavingsBadge) dom.detailsKpiSavingsBadge.textContent = `${data.energy.saving_pct.toFixed(1)}% Saved`;
}

function renderKPIs(data) {
  renderDemoKPIs(data);
  renderDetailsKPIs(data);
}

function setFlagChip(elem, active) {
  if (!elem) return;
  if (active) {
    elem.classList.add("active");
  } else {
    elem.classList.remove("active");
  }
}

// ============================================================================
// Waveform Chart Controller (Chart.js)
// ============================================================================

function createOrUpdateChart(canvasElem, isDemo, data) {
  if (!canvasElem || !window.Chart) return null;

  const fs = data.meta.fs_hz || 125.0;
  const rawAdc = data.signal.raw_adc;
  const filteredQ15 = data.signal.filtered_q15;
  const peaks = new Set(data.signal.peaks);

  const totalPoints = rawAdc.length;
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

    let hasPeak = false;
    for (let k = 0; k < stride && (i + k) < totalPoints; k++) {
      if (peaks.has(i + k)) {
        hasPeak = true;
        break;
      }
    }
    peakPoints.push(hasPeak ? filteredQ15[i] : null);
  }

  const isDark = state.theme === "dark";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";
  const textColor = isDark ? "#94a3b8" : "#64748b";

  const showAdc = isDemo ? dom.chkShowAdc.checked : (dom.chkDetailsShowAdc ? dom.chkDetailsShowAdc.checked : true);
  const showFiltered = isDemo ? dom.chkShowFiltered.checked : (dom.chkDetailsShowFiltered ? dom.chkDetailsShowFiltered.checked : true);
  const showPeaks = isDemo ? dom.chkShowPeaks.checked : (dom.chkDetailsShowPeaks ? dom.chkDetailsShowPeaks.checked : true);

  return new window.Chart(canvasElem.getContext("2d"), {
    type: "line",
    data: {
      labels: timeLabels,
      datasets: [
        {
          label: "Raw 12-bit ADC",
          data: adcData,
          borderColor: isDark ? "#60a5fa" : "#3b82f6",
          borderWidth: 1.5,
          pointRadius: 0,
          yAxisID: "yADC",
          hidden: !showAdc,
          tension: 0.1,
        },
        {
          label: "Filtered Q15 (ARM Routine)",
          data: filteredData,
          borderColor: "#0d9488",
          borderWidth: 2,
          pointRadius: 0,
          yAxisID: "yQ15",
          hidden: !showFiltered,
          tension: 0.1,
        },
        {
          label: "Detected Systolic Peaks",
          data: peakPoints,
          borderColor: "transparent",
          backgroundColor: "#e11d48",
          pointRadius: showPeaks ? 5 : 0,
          pointHoverRadius: 7,
          showLine: false,
          yAxisID: "yQ15",
          hidden: !showPeaks,
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
              if (item.datasetIndex === 2 && item.raw !== null) return ` ● Systolic Peak Detected`;
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
          title: { display: true, text: "Q15 Amplitude", color: "#0d9488" },
          grid: { color: gridColor },
          ticks: { color: textColor },
        },
        yADC: {
          type: "linear",
          position: "right",
          title: { display: true, text: "12-bit ADC Integer", color: textColor },
          grid: { drawOnChartArea: false },
          ticks: { color: textColor },
          min: 0,
          max: 4095,
        },
      },
    },
  });
}

function renderDemoWaveformChart(data) {
  if (!window.Chart || !data || !data.signal || !dom.waveformChart) return;
  if (state.demoChartInstance) {
    state.demoChartInstance.destroy();
    state.demoChartInstance = null;
  }
  state.demoChartInstance = createOrUpdateChart(dom.waveformChart, true, data);
  if (state.currentView === "demo") {
    state.chartInstance = state.demoChartInstance;
  }
}

function renderDetailsWaveformChart(data) {
  if (!window.Chart || !data || !data.signal || !dom.detailsWaveformChart) return;
  if (state.detailsChartInstance) {
    state.detailsChartInstance.destroy();
    state.detailsChartInstance = null;
  }
  state.detailsChartInstance = createOrUpdateChart(dom.detailsWaveformChart, false, data);
  if (state.currentView === "details") {
    state.chartInstance = state.detailsChartInstance;
  }
}

function renderWaveformChart(data) {
  if (state.currentView === "demo") {
    renderDemoWaveformChart(data);
  } else {
    renderDetailsWaveformChart(data);
  }
}

function updateChartDatasetVisibility(isDemo = true) {
  const chart = isDemo ? state.demoChartInstance : state.detailsChartInstance;
  if (!chart) return;
  const showAdc = isDemo ? dom.chkShowAdc.checked : (dom.chkDetailsShowAdc ? dom.chkDetailsShowAdc.checked : true);
  const showFiltered = isDemo ? dom.chkShowFiltered.checked : (dom.chkDetailsShowFiltered ? dom.chkDetailsShowFiltered.checked : true);
  const showPeaks = isDemo ? dom.chkShowPeaks.checked : (dom.chkDetailsShowPeaks ? dom.chkDetailsShowPeaks.checked : true);

  chart.setDatasetVisibility(0, showAdc);
  chart.setDatasetVisibility(1, showFiltered);
  chart.setDatasetVisibility(2, showPeaks);
  chart.getDatasetMeta(2).pointRadius = showPeaks ? 5 : 0;
  chart.update("none");
}

// ============================================================================
// Concept Subsystems Rendering (Tabs in Details View)
// ============================================================================

// --- Tab 1: Number Representation ---
function renderNumberRepresentation(data) {
  const num = data.number_representation;
  if (!num) return;

  dom.numLastAdc.textContent = `${num.last_adc_raw} (${(num.last_adc_raw / 4095.0 * 3.3).toFixed(3)} V)`;
  dom.numLastAdcHex.textContent = num.last_adc_hex;

  dom.numLastQ15.textContent = `${num.last_q15_signed} (${(num.last_q15_signed / 32768.0).toFixed(4)})`;
  dom.numLastQ15Hex.textContent = num.last_q15_hex;

  dom.numLastFiltered.textContent = `${num.last_filtered_q15} (${(num.last_filtered_q15 / 32768.0).toFixed(4)})`;
  dom.numLastFilteredHex.textContent = num.last_filtered_hex;
}

// --- Tab 2: ALU & Flags ---
function renderAluFlags(data) {
  const alu = data.alu;
  if (!alu) return;

  const flags = alu.flags;
  setLedFlag(dom.ledFlagN, flags.N);
  setLedFlag(dom.ledFlagZ, flags.Z);
  setLedFlag(dom.ledFlagC, flags.C);
  setLedFlag(dom.ledFlagV, flags.V);

  dom.aluResultVal.textContent = alu.cmp_result;
  dom.aluResultHex.textContent = alu.cmp_result_hex;

  if (alu.branch_taken) {
    dom.aluBranchEval.textContent = `TAKEN -> Heart rate (${alu.bpm}) > Threshold (${alu.threshold}) -> ALERT!`;
    dom.aluBranchEval.className = "branch-eval-box branch-taken";
  } else {
    dom.aluBranchEval.textContent = `NOT TAKEN -> Heart rate (${alu.bpm}) <= Threshold (${alu.threshold}) -> Normal`;
    dom.aluBranchEval.className = "branch-eval-box branch-not-taken";
  }
}

function setLedFlag(ledElem, active) {
  if (!ledElem) return;
  if (active) {
    ledElem.classList.add("active");
  } else {
    ledElem.classList.remove("active");
  }
}

// --- Tab 3: ARM Core & Stepper ---
function renderArmCore(data) {
  const arm = data.arm;
  if (!arm) return;

  dom.armStepSummary.textContent = `${arm.instruction_count} instructions executed for 4-tap boxcar moving average kernel.`;

  if (arm.matches_python) {
    dom.armVerificationStatus.innerHTML = `<span class="badge badge-success">UNIFIED CO-SIMULATION PASS</span> Emulated ARM Thumb output matches Python vector bit-for-bit.`;
  } else {
    dom.armVerificationStatus.innerHTML = `<span class="badge badge-alert">MISMATCH DETECTED</span> Emulation divergence.`;
  }

  state.armStepIndex = 0;
  updateArmStepDisplay();
}

function updateArmStepDisplay() {
  const activeData = state.detailsResult || state.demoResult;
  if (!activeData || !activeData.arm || !activeData.arm.steps) return;
  const steps = activeData.arm.steps;
  const total = steps.length;
  if (total === 0) return;

  const idx = Math.min(Math.max(0, state.armStepIndex), total - 1);
  state.armStepIndex = idx;

  dom.stepCounterText.textContent = `Step ${idx + 1} of ${total}`;

  dom.btnStepFirst.disabled = idx === 0;
  dom.btnStepPrev.disabled = idx === 0;
  dom.btnStepNext.disabled = idx === total - 1;
  dom.btnStepLast.disabled = idx === total - 1;

  dom.armStepTableBody.innerHTML = "";
  steps.forEach((step, sIdx) => {
    const tr = document.createElement("tr");
    if (sIdx === idx) tr.classList.add("stepper-active-row");

    tr.innerHTML = `
      <td>${step.step}</td>
      <td><code>0x${step.pc.toString(16).toUpperCase()}</code></td>
      <td><strong>${escapeHtml(step.disasm)}</strong></td>
      <td><code>0x${(step.registers.r0 >>> 0).toString(16).padStart(8, '0').toUpperCase()}</code></td>
      <td><code>0x${(step.registers.r1 >>> 0).toString(16).padStart(8, '0').toUpperCase()}</code></td>
      <td><code>0x${(step.registers.r2 >>> 0).toString(16).padStart(8, '0').toUpperCase()}</code></td>
      <td><code>0x${(step.registers.r3 >>> 0).toString(16).padStart(8, '0').toUpperCase()}</code></td>
    `;
    dom.armStepTableBody.appendChild(tr);
  });
}

function stepARMInstruction(action) {
  const activeData = state.detailsResult || state.demoResult;
  if (!activeData || !activeData.arm || !activeData.arm.steps) return;
  const total = activeData.arm.steps.length;

  if (action === "first") state.armStepIndex = 0;
  else if (action === "prev") state.armStepIndex = Math.max(0, state.armStepIndex - 1);
  else if (action === "next") state.armStepIndex = Math.min(total - 1, state.armStepIndex + 1);
  else if (action === "last") state.armStepIndex = total - 1;

  updateArmStepDisplay();
}

// --- Tab 4: Cache Hierarchy ---
function renderCache(data) {
  const c = data.cache;
  if (!c) return;

  dom.cacheLinesTotal.textContent = c.num_lines;
  dom.cacheOffsetBits.textContent = c.offset_bits;
  dom.cacheIndexBits.textContent = c.index_bits;
  dom.cacheTagBits.textContent = c.tag_bits;

  dom.cacheTotalHits.textContent = c.hits;
  dom.cacheTotalMisses.textContent = c.misses;

  const hitPct = (c.hit_rate * 100).toFixed(1);
  dom.cacheHitRatePct.textContent = `${hitPct}%`;
  dom.cacheAmatValue.textContent = `${c.amat_cycles.toFixed(2)} cycles`;

  dom.cacheBarHit.style.width = `${hitPct}%`;
  dom.cacheBarMiss.style.width = `${(100 - parseFloat(hitPct)).toFixed(1)}%`;
}

// --- Tab 5: Serial I/O ---
function renderSerial(data) {
  const s = data.serial;
  if (!s) return;

  dom.uartBaudRate.textContent = `${s.uart.baud_rate} Baud (bps)`;
  dom.uartByteRate.textContent = `${s.uart.bytes_per_second} B/s`;
  dom.uartUtilPct.textContent = `${s.uart.bus_utilization_pct.toFixed(2)}%`;
  dom.uartPacketHex.textContent = s.uart.sample_packet_hex;

  dom.i2cClkFreq.textContent = `${s.i2c.clock_hz / 1000} kHz`;
  dom.i2cByteRate.textContent = `${s.i2c.bytes_per_second} B/s`;
  dom.i2cDutyPct.textContent = `${s.i2c.bus_duty_cycle_pct.toFixed(2)}%`;
}

// --- Tab 6: Duty-Cycle Energy ---
function renderEnergy(data) {
  const e = data.energy;
  if (!e) return;

  dom.energyActiveCurrent.textContent = `${e.active_current_ua.toFixed(1)} µA`;
  dom.energySleepCurrent.textContent = `${e.sleep_current_ua.toFixed(1)} µA`;
  dom.energyAvgCurrent.textContent = `${e.avg_current_ua.toFixed(1)} µA`;
  dom.energyBaselineCurrent.textContent = `${e.baseline_always_on_ua.toFixed(1)} µA`;
  dom.energySavingPct.textContent = `${e.saving_pct.toFixed(1)}%`;
  dom.energySourceText.textContent = e.source;

  if (e.placeholder) {
    dom.placeholderBanner.style.display = "block";
  } else {
    dom.placeholderBanner.style.display = "none";
  }
}

// --- Tab 7: Verification Suite ---
async function loadVerification() {
  try {
    const data = await fetchJson("/api/verification");
    state.verificationData = data;

    // 1. Q15 check
    const q15 = data.checks.q15_vs_float;
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
  const passSvg = '<svg class="verify-icon-svg text-success" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';
  const failSvg = '<svg class="verify-icon-svg text-danger" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
  if (passed) {
    badgeElem.textContent = "PASSED";
    badgeElem.className = "verify-status-badge badge-success";
    iconElem.innerHTML = passSvg;
  } else {
    badgeElem.textContent = "FAILED";
    badgeElem.className = "verify-status-badge badge-alert";
    iconElem.innerHTML = failSvg;
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ============================================================================
// Guided Tour Controller (5 Short Steps)
// ============================================================================

const tourSteps = [
  {
    title: "1. Physiological Signal Acquisition",
    body: "Photoplethysmography (PPG) waveforms are sampled from an optical sensor over an I2C bus at 125 Hz. Samples are converted into 12-bit unsigned integers (0 to 4095) representing raw arterial blood volume pulses."
  },
  {
    title: "2. Q15 Fixed-Point Conversion",
    body: "Because microcontrollers lack double-precision floating point hardware, samples are centered and scaled into signed Q15 format (-1.0 to +0.9999). This represents fractional decimals as 16-bit integers with zero division overhead."
  },
  {
    title: "3. ARM Thumb-2 Moving Average",
    body: "An emulated ARM Cortex-M routine loads halfwords from memory, sums adjacent samples with <code>ADDS</code>, and performs an arithmetic right-shift <code>ASRS #2</code> to execute a 4-tap boxcar filter eliminating high-frequency motion artifacts."
  },
  {
    title: "4. Hardware Cache & Memory AMAT",
    body: "Filter memory accesses pass through a simulated L1 SRAM cache. Spatial and temporal locality keep hit rates above 90%, slashing Average Memory Access Time (AMAT) from 20 wait-state cycles down to near 1 cycle."
  },
  {
    title: "5. ALU Thresholding & Low-Power Telemetry",
    body: "The calculated heart rate is compared against safety limits using an ALU <code>CMP</code> instruction. When exceeding the threshold, condition flags trigger a branch (BGT) alert, and packets are dispatched over UART while duty-cycling the CPU in sleep mode."
  }
];

function openTour() {
  state.tourCurrentStep = 0;
  dom.tourModal.style.display = "flex";
  renderTourStep();
}

function closeTour() {
  dom.tourModal.style.display = "none";
}

function renderTourStep() {
  const step = tourSteps[state.tourCurrentStep];
  dom.tourStepTitle.textContent = step.title;
  dom.tourStepIndicator.textContent = `Step ${state.tourCurrentStep + 1} of ${tourSteps.length}`;
  dom.tourStepBody.innerHTML = step.body;

  dom.btnTourPrev.disabled = state.tourCurrentStep === 0;
  dom.btnTourNext.innerHTML = state.tourCurrentStep === tourSteps.length - 1 ? "Finish" : 'Next <svg class="icon" viewBox="0 0 24 24"><polygon points="5 4 15 12 5 20 5 4"/></svg>';
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
// Data Export (JSON & CSV)
// ============================================================================

function exportSimulationJson() {
  const resultData = state.detailsResult || state.demoResult || state.lastResult;
  if (!resultData) {
    showErrorBanner("No simulation data available to export. Run a simulation first.");
    return;
  }
  const payload = JSON.stringify(resultData, null, 2);
  downloadBlob(payload, `wearable_sim_${Date.now()}.json`, "application/json");
}

function exportSignalCsv() {
  const resultData = state.detailsResult || state.demoResult || state.lastResult;
  if (!resultData || !resultData.signal) {
    showErrorBanner("No signal data available to export. Run a simulation first.");
    return;
  }

  const sig = resultData.signal;
  const fs = resultData.meta.fs_hz || 125.0;
  const peaks = new Set(sig.peaks);

  const lines = ["time_s,raw_adc,filtered_q15,is_systolic_peak"];
  for (let i = 0; i < sig.raw_adc.length; i++) {
    const t = (i / fs).toFixed(4);
    const raw = sig.raw_adc[i];
    const filt = sig.filtered_q15[i];
    const isPeak = peaks.has(i) ? 1 : 0;
    lines.push(`${t},${raw},${filt},${isPeak}`);
  }

  downloadBlob(lines.join("\n"), `wearable_ppg_signal_${Date.now()}.csv`, "text/csv");
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
// Theme Management (Light & Dark with SVG Icon)
// ============================================================================

function setupTheme() {
  const saved = localStorage.getItem("theme");
  // Default to clean light mode unless user explicitly selected dark previously
  const theme = saved ? saved : "light";
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
  const sunSvg = '<svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';
  const moonSvg = '<svg class="icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  dom.themeToggle.innerHTML = theme === "dark" ? sunSvg : moonSvg;
  dom.themeToggle.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} mode`);

  // Re-render charts if they exist to adapt gridlines & axes
  if (state.demoResult && dom.waveformChart && state.currentView === "demo") {
    renderDemoWaveformChart(state.demoResult);
  }
  if (state.detailsResult && dom.detailsWaveformChart && state.currentView === "details") {
    renderDetailsWaveformChart(state.detailsResult);
  }
}

// Entrypoint initialization on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  initializeApp();
});
