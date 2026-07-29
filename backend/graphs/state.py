"""
backend/graphs/state.py

Defines the single shared State object that flows through every node
in the TriageFlow LangGraph workflow.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypedDict
from uuid import uuid4


class TicketState(TypedDict):
    ticket_id: str
    raw_text: str
    classification: dict[str, Any] | None
    safety_override_applied: bool
    retrieved_chunks: list[dict[str, Any]]
    inventory_check: dict[str, Any] | None
    draft_recommendation: str | None
    human_decision: str | None
    human_feedback: str | None
    status: str
    created_at: str
    updated_at: str


def create_initial_state(raw_text: str) -> TicketState:
    """
    Build a fresh TicketState for a brand-new incoming ticket.
    """
    now = datetime.now(UTC).isoformat()

    return {
        "ticket_id": str(uuid4()),
        "raw_text": raw_text,
        "classification": None,
        "safety_override_applied": False,
        "retrieved_chunks": [],
        "inventory_check": None,
        "draft_recommendation": None,
        "human_decision": None,
        "human_feedback": None,
        "status": "processing",
        "created_at": now,
        "updated_at": now,
    }


if __name__ == "__main__":
    state = create_initial_state("Pump P-204 making loud noise, vibration increasing.")
    for key, value in state.items():
        print(f"{key}: {value!r}")
