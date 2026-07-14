"""
backend/graphs/state.py

Defines the single shared State object that flows through every node
in the TriageFlow LangGraph workflow.
"""

from __future__ import annotations

from typing import TypedDict, Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone


class TicketState(TypedDict):
    ticket_id: str
    raw_text: str
    classification: Optional[Dict[str, Any]]
    safety_override_applied: bool
    retrieved_chunks: List[Dict[str, Any]]
    inventory_check: Optional[Dict[str, Any]]
    draft_recommendation: Optional[str]
    human_decision: Optional[str]
    human_feedback: Optional[str]
    status: str
    created_at: str
    updated_at: str


def create_initial_state(raw_text: str) -> "TicketState":
    """
    Build a fresh TicketState for a brand-new incoming ticket.
    """
    now = datetime.now(timezone.utc).isoformat()

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
