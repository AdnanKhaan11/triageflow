// frontend/sensor_monitor.js
// Real-time sensor monitoring dashboard logic

const EQUIPMENT_LIST = [
  { id: "P-204", name: "Pump P-204", type: "Centrifugal Pump" },
  { id: "P-207", name: "Pump P-207", type: "Vertical Pump" },
  { id: "C-11", name: "Compressor C-11", type: "Reciprocating Compressor" },
  { id: "M-18", name: "Motor M-18", type: "Induction Motor" },
  { id: "T-501", name: "Turbine T-501", type: "Steam Turbine" },
];

let simInterval = null;
let totalReadings = 0;
let totalAnomalies = 0;
let totalTickets = 0;
let totalHealthy = 0;
let equipmentState = {};

// ── Init ──────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  initSensorCards();
  checkPipelineStatus();
});

function initSensorCards() {
  const grid = document.getElementById("sensor-grid");
  if (!grid) return;
  grid.innerHTML = EQUIPMENT_LIST.map(
    (eq) => `
    <div class="sensor-card" id="card-${eq.id}">
      <div class="sensor-card-header">
        <span class="equipment-id">${eq.id}</span>
        <span class="status-indicator">
          <span class="status-dot-live green" id="dot-${eq.id}"></span>
          <span id="status-${eq.id}">Standby</span>
        </span>
      </div>
      <div style="font-size:0.72rem;color:var(--text-muted);
                  margin-bottom:0.75rem;">${eq.type}</div>
      <div class="metric-row">
        <div class="metric">
          <div class="metric-label">RMS</div>
          <div class="metric-value" id="rms-${eq.id}">—</div>
        </div>
        <div class="metric">
          <div class="metric-label">Kurtosis</div>
          <div class="metric-value" id="kurt-${eq.id}">—</div>
        </div>
        <div class="metric">
          <div class="metric-label">Severity</div>
          <div class="metric-value" id="sev-${eq.id}">—</div>
        </div>
      </div>
      <div class="anomaly-bar-wrap">
        <div class="anomaly-bar" id="bar-${eq.id}"
             style="width:0%;background:var(--green);"></div>
      </div>
      <div style="display:flex;justify-content:space-between;
                  align-items:center;">
        <span class="fault-label" id="fault-${eq.id}">Fault: —</span>
        <span class="ticket-id" id="prob-${eq.id}">prob: —</span>
      </div>
    </div>
  `,
  ).join("");
}

// ── Backend health check ──────────────────────────────────────
async function checkBackendHealth() {
  const dot = document.getElementById("status-dot");
  const text = document.getElementById("status-text");
  try {
    await checkHealth();
    if (dot) dot.style.background = "var(--green)";
    if (text) text.textContent = "API Online";
  } catch {
    if (dot) {
      dot.style.background = "var(--red)";
      dot.style.animation = "none";
    }
    if (text) text.textContent = "API Offline";
  }
}

// ── Pipeline status ───────────────────────────────────────────
async function checkPipelineStatus() {
  try {
    const resp = await apiFetch("/sensors/status");
    if (resp.status === "ready") {
      addLog(
        `Pipeline ready on ${resp.device} | ` +
          `threshold=${resp.anomaly_threshold}`,
        "normal",
      );
    } else {
      addLog(`Pipeline unavailable: ${resp.error}`, "fault");
    }
  } catch {
    addLog(
      "Sensor pipeline not connected — " + "models may not be loaded",
      "fault",
    );
  }
}

// ── Simulation ────────────────────────────────────────────────
function startSimulation() {
  const equipId = document.getElementById("equipment-select").value;
  const mode = document.getElementById("mode-select").value;
  const btn = document.getElementById("btn-simulate");
  const stop = document.getElementById("btn-stop");
  const status = document.getElementById("sim-status");

  btn.style.display = "none";
  stop.style.display = "inline-flex";
  status.textContent = `Running — ${equipId}`;

  addLog(`Simulation started: ${equipId} [mode=${mode}]`, "normal");

  let tick = 0;
  simInterval = setInterval(async () => {
    tick++;
    const isFault = shouldInjectFault(mode, tick);
    await runOneSensorReading(equipId, isFault);
  }, 1500);
}

function stopSimulation() {
  if (simInterval) clearInterval(simInterval);
  simInterval = null;
  document.getElementById("btn-simulate").style.display = "inline-flex";
  document.getElementById("btn-stop").style.display = "none";
  document.getElementById("sim-status").textContent = "Stopped";
  addLog("Simulation stopped", "normal");
}

function shouldInjectFault(mode, tick) {
  if (mode === "healthy") return false;
  if (mode === "fault") return true;
  return tick % 4 === 0; // mixed: every 4th reading is a fault
}

// ── Core: call API and update UI ──────────────────────────────
async function runOneSensorReading(equipId, isFault) {
  const signal = isFault ? generateFaultSignal() : generateHealthySignal();

  totalReadings++;
  updateStat("stat-total", totalReadings);

  try {
    const result = await apiFetch("/sensors/analyze", {
      method: "POST",
      body: JSON.stringify({
        equipment_id: equipId,
        signal: Array.from(signal),
        sampling_rate: 20480,
      }),
    });

    updateSensorCard(result);

    if (result.is_anomaly) {
      totalAnomalies++;
      updateStat("stat-anomalies", totalAnomalies);
      if (result.ticket_created) {
        totalTickets++;
        updateStat("stat-tickets", totalTickets);
        showToast(
          `Ticket created: ${result.fault_type} on ${equipId}`,
          "error",
        );
      }
      addLog(
        `⚠ ANOMALY ${equipId} | fault=${result.fault_type} | ` +
          `sev=${result.severity} | prob=${result.anomaly_probability}`,
        "fault",
      );
    } else {
      totalHealthy++;
      updateStat("stat-healthy", totalHealthy);
      addLog(
        `✓ Normal ${equipId} | rms=${result.rms} | ` +
          `kurt=${result.kurtosis}`,
        "normal",
      );
    }
  } catch (err) {
    addLog(`Error reading ${equipId}: ${err.message}`, "fault");

    // Fallback: simulate locally if API unavailable
    simulateLocally(equipId, isFault);
  }
}

// ── Update sensor card UI ─────────────────────────────────────
function updateSensorCard(result) {
  const id = result.equipment_id;
  const card = document.getElementById(`card-${id}`);
  if (!card) return;

  const isAnomaly = result.is_anomaly;
  const prob = result.anomaly_probability;
  const sev = result.severity || "low";

  card.className = `sensor-card ${isAnomaly ? "anomaly" : "healthy"}`;

  const dot = document.getElementById(`dot-${id}`);
  if (dot) {
    dot.className = `status-dot-live ${isAnomaly ? "red" : "green"}`;
  }

  setText(`status-${id}`, isAnomaly ? "ANOMALY" : "Healthy");
  setText(`rms-${id}`, result.rms?.toFixed(4) ?? "—");
  setText(`kurt-${id}`, result.kurtosis?.toFixed(2) ?? "—");
  setText(`sev-${id}`, sev.toUpperCase());
  setText(`fault-${id}`, `Fault: ${result.fault_type}`);
  setText(`prob-${id}`, `prob: ${prob?.toFixed(4) ?? "—"}`);

  const bar = document.getElementById(`bar-${id}`);
  if (bar) {
    bar.style.width = `${Math.min(prob * 100, 100)}%`;
    bar.style.background = isAnomaly ? "var(--red)" : "var(--green)";
  }

  const sevEl = document.getElementById(`sev-${id}`);
  if (sevEl) {
    const colors = {
      low: "var(--green)",
      medium: "var(--blue)",
      high: "var(--yellow)",
      critical: "var(--red)",
    };
    sevEl.style.color = colors[sev] || "var(--text-primary)";
  }
}

// ── Simulate locally (when API is down) ──────────────────────
function simulateLocally(equipId, isFault) {
  const prob = isFault ? 0.7 + Math.random() * 0.3 : Math.random() * 0.05;
  const rms = isFault ? 0.3 + Math.random() * 0.3 : 0.04 + Math.random() * 0.02;

  updateSensorCard({
    equipment_id: equipId,
    is_anomaly: isFault,
    anomaly_probability: parseFloat(prob.toFixed(4)),
    fault_type: isFault ? "OR_007" : "Normal",
    fault_confidence: 0.85,
    severity: isFault ? "high" : "low",
    rms: parseFloat(rms.toFixed(4)),
    kurtosis: isFault ? 8.2 : 1.1,
    peak_to_peak: rms * 8,
    ticket_created: false,
  });
}

// ── Signal generators ─────────────────────────────────────────
function generateHealthySignal(n = 20480) {
  const out = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    out[i] =
      (Math.random() - 0.5) * 0.1 +
      0.05 * Math.sin((2 * Math.PI * 33.3 * i) / 20480);
  }
  return out;
}

function generateFaultSignal(n = 20480) {
  const out = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    out[i] =
      (Math.random() - 0.5) * 0.1 +
      0.3 * Math.sin((2 * Math.PI * 120 * i) / 20480) +
      (i % 170 === 0 ? (Math.random() > 0.5 ? 1.2 : -1.2) : 0);
  }
  return out;
}

// ── Log ───────────────────────────────────────────────────────
function addLog(message, type = "normal") {
  const log = document.getElementById("stream-log");
  if (!log) return;
  const now = new Date().toLocaleTimeString();
  const cls = type === "fault" ? "log-fault" : "log-normal";
  const entry = document.createElement("div");
  entry.className = "log-entry";
  entry.innerHTML =
    `<span class="log-time">${now}</span>` +
    `<span class="${cls}">${escapeHtml(message)}</span>`;
  log.insertBefore(entry, log.firstChild);
  if (log.children.length > 200) {
    log.removeChild(log.lastChild);
  }
}

function clearLog() {
  const log = document.getElementById("stream-log");
  if (log) log.innerHTML = "";
}

// ── Helpers ───────────────────────────────────────────────────
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function updateStat(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
