"""
backend/api/routes/tickets.py
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langgraph.types import Command

from backend.db.models import Ticket
from backend.db.session import get_db
from backend.graphs.state import create_initial_state
from backend.graphs.triage_graph import get_triage_graph

router = APIRouter(prefix="/tickets", tags=["tickets"])

graph = get_triage_graph()


class CreateTicketRequest(BaseModel):
    raw_text: str


class DecisionRequest(BaseModel):
    decision: str
    feedback: str | None = None
    edited_recommendation: str | None = None


@router.post("/")
def create_ticket(
    request: CreateTicketRequest,
    db: Session = Depends(get_db),
):
    state = create_initial_state(request.raw_text)
    ticket_id = state["ticket_id"]
    thread_id = f"ticket-{ticket_id}"
    config = {"configurable": {"thread_id": thread_id}}

    graph.invoke(state, config=config)

    db_ticket = Ticket(
        ticket_id=ticket_id,
        raw_text=request.raw_text,
        status="awaiting_review",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_ticket)
    db.commit()

    return {"ticket_id": ticket_id, "status": "awaiting_review"}


@router.get("/")
def list_tickets(
    status: str = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)

    tickets = query.order_by(Ticket.created_at.desc()).all()

    results = []
    for ticket in tickets:
        thread_id = f"ticket-{ticket.ticket_id}"
        config = {"configurable": {"thread_id": thread_id}}

        checkpoint = graph.get_state(config)
        graph_state = checkpoint.values if checkpoint else {}

        results.append(
            {
                "ticket_id": ticket.ticket_id,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
                "state": graph_state,
            }
        )

    return {"status": status, "tickets": results}


@router.get("/history")
def get_ticket_history(
    db: Session = Depends(get_db),
):
    """
    Returns all closed/decided tickets for the history view.
    """
    closed_statuses = ["closed", "closed_rejected"]

    tickets = (
        db.query(Ticket)
        .filter(Ticket.status.in_(closed_statuses))
        .order_by(Ticket.updated_at.desc())
        .all()
    )

    results = []
    for ticket in tickets:
        thread_id = f"ticket-{ticket.ticket_id}"
        config = {"configurable": {"thread_id": thread_id}}

        checkpoint = graph.get_state(config)
        graph_state = checkpoint.values if checkpoint else {}

        results.append(
            {
                "ticket_id": ticket.ticket_id,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "state": graph_state,
            }
        )

    return {"tickets": results}


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    thread_id = f"ticket-{ticket_id}"
    config = {"configurable": {"thread_id": thread_id}}

    checkpoint = graph.get_state(config)

    if checkpoint is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {"ticket_id": ticket_id, "state": checkpoint.values}


@router.post("/{ticket_id}/decision")
def submit_decision(
    ticket_id: str,
    request: DecisionRequest,
    db: Session = Depends(get_db),
):
    thread_id = f"ticket-{ticket_id}"
    config = {"configurable": {"thread_id": thread_id}}

    result = graph.invoke(
        Command(
            resume={
                "decision": request.decision,
                "feedback": request.feedback,
            }
        ),
        config=config,
    )

    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket:
        db_ticket.status = result.get("status", "closed")
        db_ticket.updated_at = datetime.now(timezone.utc)
        db.commit()

    return {
        "ticket_id": ticket_id,
        "status": result.get("status"),
        "human_decision": request.decision,
    }


@router.get("/{ticket_id}/audit-log")
def get_audit_log(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    return {"ticket_id": ticket_id, "audit_log": [], "message": "not implemented yet"}
