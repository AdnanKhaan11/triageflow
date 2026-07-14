"""
apps/frontend/utils/api_client.py

RESPONSIBILITY
---------------
A thin wrapper around HTTP calls to your FastAPI backend. The
Streamlit pages call functions from THIS file, never `requests.get/post`
directly — this is what keeps your UI code decoupled from the exact
API shape, and gives you ONE place to update if an endpoint URL or
response shape changes.

TODO
-----
Write one function per backend endpoint (see triageFlow_plan.md
section 13 for the exact shapes):

    def create_ticket(raw_text: str) -> dict:
        # POST /tickets
        ...

    def get_ticket(ticket_id: str) -> dict:
        # GET /tickets/{ticket_id}
        ...

    def list_tickets(status: str | None = None) -> list[dict]:
        # GET /tickets?status=...
        ...

    def submit_decision(ticket_id: str, decision: str, **kwargs) -> dict:
        # POST /tickets/{ticket_id}/decision
        ...

    def get_audit_log(ticket_id: str) -> list[dict]:
        # GET /tickets/{ticket_id}/audit-log
        ...

HINTS
------
- Read the backend API base URL from an environment variable or a
  simple config constant, not hard-coded inline in every function —
  this matters once you deploy frontend and backend separately.
- Decide how you want to handle errors (a non-200 response) — at
  minimum, don't let a backend error crash the Streamlit app with an
  unhandled exception; show the user something reasonable.

LEARNING RESOURCES
--------------------
- `requests` library docs (or `httpx` if you prefer async-capable
  client, though Streamlit's typical synchronous model means
  `requests` is simpler here).

COMMON MISTAKES
-----------------
- Scattering raw `requests.post(...)` calls throughout multiple page
  files instead of centralizing them here — makes it painful to
  change the API base URL or add shared error handling later.
"""

from __future__ import annotations

import os

API_BASE_URL = os.environ.get("TRIAGEFLOW_API_URL", "http://localhost:8000")


def create_ticket(raw_text: str) -> dict:
    """TODO: implement — see module docstring."""
    raise NotImplementedError("Implement create_ticket")


def get_ticket(ticket_id: str) -> dict:
    """TODO: implement — see module docstring."""
    raise NotImplementedError("Implement get_ticket")


def list_tickets(status: str | None = None) -> list:
    """TODO: implement — see module docstring."""
    raise NotImplementedError("Implement list_tickets")


def submit_decision(ticket_id: str, decision: str, **kwargs) -> dict:
    """TODO: implement — see module docstring."""
    raise NotImplementedError("Implement submit_decision")


def get_audit_log(ticket_id: str) -> list:
    """TODO: implement — see module docstring."""
    raise NotImplementedError("Implement get_audit_log")
