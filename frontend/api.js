// frontend/api.js
// Centralized API client — all fetch() calls go through here.
// Same concept as backend/services/llm_client.py: one place to
// change if the base URL or request format ever changes.

const API_BASE = "http://localhost:8000";

// -----------------------------------------------------------------------
// Helper: makes a fetch call, parses JSON, throws on non-2xx responses
// so callers don't need to check response.ok themselves.
// -----------------------------------------------------------------------
async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      errorDetail = body.detail || JSON.stringify(body);
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return response.json();
}
// GET /tickets/history
// Returns all closed/decided tickets
async function getTicketHistory() {
  return apiFetch("/tickets/history");
}

// -----------------------------------------------------------------------
// POST /tickets/
// Submits a new maintenance ticket.
// Returns: { ticket_id, status }
// -----------------------------------------------------------------------
async function createTicket(rawText) {
  return apiFetch("/tickets/", {
    method: "POST",
    body: JSON.stringify({ raw_text: rawText }),
  });
}

// -----------------------------------------------------------------------
// GET /tickets/{ticket_id}
// Gets the current state of a ticket (including draft recommendation
// and classification once the graph has run).
// Returns: { ticket_id, state }
// -----------------------------------------------------------------------
async function getTicket(ticketId) {
  return apiFetch(`/tickets/${ticketId}`);
}

// -----------------------------------------------------------------------
// GET /tickets?status=awaiting_review
// Lists tickets filtered by status.
// Returns: { status, tickets }
// -----------------------------------------------------------------------
async function listTickets(status = null) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiFetch(`/tickets/${query}`);
}

// -----------------------------------------------------------------------
// POST /tickets/{ticket_id}/decision
// Submits the human reviewer's decision and resumes the graph.
// Returns: { ticket_id, status, human_decision }
// -----------------------------------------------------------------------
async function submitDecision(
  ticketId,
  decision,
  feedback = null,
  editedRecommendation = null,
) {
  return apiFetch(`/tickets/${ticketId}/decision`, {
    method: "POST",
    body: JSON.stringify({
      decision,
      feedback,
      edited_recommendation: editedRecommendation,
    }),
  });
}

// -----------------------------------------------------------------------
// GET /tickets/{ticket_id}/audit-log
// Retrieves the full audit trail for a ticket.
// Returns: { ticket_id, audit_log }
// -----------------------------------------------------------------------
async function getAuditLog(ticketId) {
  return apiFetch(`/tickets/${ticketId}/audit-log`);
}

// -----------------------------------------------------------------------
// GET /health
// Quick backend connectivity check.
// -----------------------------------------------------------------------
async function checkHealth() {
  return apiFetch("/health");
}

// -----------------------------------------------------------------------
// UI Helper: show a toast notification
// -----------------------------------------------------------------------
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const icon = type === "success" ? "✓" : type === "error" ? "✗" : "ℹ";
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slide-in 0.2s ease reverse";
    setTimeout(() => toast.remove(), 200);
  }, 3500);
}

// -----------------------------------------------------------------------
// UI Helper: get urgency badge HTML
// -----------------------------------------------------------------------
function urgencyBadge(urgency) {
  if (!urgency) return "";
  const cls = `badge badge-${urgency.toLowerCase()}`;
  return `<span class="${cls}">${urgency.toUpperCase()}</span>`;
}
