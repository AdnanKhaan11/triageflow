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
// UI Helper: show a toast notification (Enhanced - Top Position)
// -----------------------------------------------------------------------
// -----------------------------------------------------------------------
// UI Helper: show a toast notification (Enhanced - Top Position)
// -----------------------------------------------------------------------
function showToast(
  message,
  type = "success",
  title = null,
  showConfirm = false,
  onConfirm = null,
) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const titles = {
    success: "Success",
    error: "Error",
    info: "Information",
    warning: "Warning",
  };

  const finalTitle = title || titles[type] || "Notification";

  const icons = {
    success: "✓",
    error: "✗",
    info: "ℹ",
    warning: "⚠",
  };

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  let contentHTML = `
    <div class="toast-icon">${icons[type] || "ℹ"}</div>
    <div class="toast-content">
      <div class="toast-title">${finalTitle}</div>
      <div class="toast-message">${message}</div>
    </div>
    <button class="toast-close" onclick="this.closest('.toast').remove()">✕</button>
    <div class="toast-progress"></div>
  `;

  toast.innerHTML = contentHTML;
  container.appendChild(toast);

  // Auto-remove with animation
  setTimeout(() => {
    toast.classList.add("toast-exit");
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
// -----------------------------------------------------------------------
// UI Helper: Add activity feed item
// -----------------------------------------------------------------------
function addActivity(message, type = "info") {
  const feed = document.getElementById("activity-feed");
  if (!feed) return;

  const dotColors = {
    success: "green",
    info: "purple",
    warning: "orange",
    error: "orange",
  };

  const item = document.createElement("div");
  item.className = "activity-item";
  item.innerHTML = `
    <span class="activity-dot ${dotColors[type] || "purple"}"></span>
    <span>${message}</span>
    <span class="activity-time">${new Date().toLocaleTimeString()}</span>
  `;

  feed.appendChild(item);

  // Keep only last 5 items
  while (feed.children.length > 5) {
    feed.removeChild(feed.firstChild);
  }

  // Auto-remove after 8 seconds
  setTimeout(() => {
    if (item.parentNode) {
      item.style.opacity = "0";
      item.style.transform = "translateX(20px)";
      item.style.transition = "all 0.3s ease";
      setTimeout(() => item.remove(), 300);
    }
  }, 8000);
}

// -----------------------------------------------------------------------
// UI Helper: get urgency badge HTML
// -----------------------------------------------------------------------
function urgencyBadge(urgency) {
  if (!urgency) return "";
  const cls = `badge badge-${urgency.toLowerCase()}`;
  return `<span class="${cls}">${urgency.toUpperCase()}</span>`;
}

// -----------------------------------------------------------------------
// DELETE /tickets/{ticket_id}
// Deletes a ticket from history
// Returns: { ticket_id, status }
// -----------------------------------------------------------------------
async function deleteTicket(ticketId) {
  return apiFetch(`/tickets/${ticketId}`, {
    method: "DELETE",
  });
}
