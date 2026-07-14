"""
backend/graphs/triage_graph.py

Assembles the TriageFlow LangGraph: nodes, edges, checkpointer,
human-in-the-loop interrupt.
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END

# from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.types import interrupt, Command

from backend.graphs.state import TicketState
from backend.agents.classifier_agent import classify_node
from backend.agents.retrieval_agent import retrieve_node
from backend.agents.inventory_agent import check_inventory_node
from backend.agents.drafting_agent import draft_node
from backend.services.safety_rules import SafetyOverride

# ---------------------------------------------------------------------
# Small "thin wrapper" nodes that don't deserve their own agent file
# ---------------------------------------------------------------------


def ingest_node(state: TicketState) -> dict:
    """Entry point. raw_text already exists in state from
    create_initial_state() — nothing to compute yet."""
    return {"status": "processing"}


def safety_check_node(state: TicketState) -> dict:
    """Wraps apply_safety_override() to match the node(state)->dict shape."""
    override = SafetyOverride()
    raw_text = state.get("raw_text", "")
    classification = state.get("classification", {})

    updated_classification = override.apply_safety_override(raw_text, classification)

    return {"classification": updated_classification}


def human_review_node(state: TicketState) -> dict:
    """
    interrupt() pauses the ENTIRE graph run here until something
    resumes it with Command(resume=...).
    """
    decision = interrupt(
        {
            "draft_recommendation": state.get("draft_recommendation"),
            "classification": state.get("classification"),
        }
    )
    return {
        "human_decision": decision.get("decision"),
        "human_feedback": decision.get("feedback"),
        "status": "awaiting_review",
    }


def finalize_node(state: TicketState) -> dict:
    """
    Sets the final status based on the human's decision, rather than
    always closing the same way regardless of outcome.
    """
    decision = state.get("human_decision")

    if decision == "reject":
        final_status = "closed_rejected"
    else:
        # "approve" and "edit" both result in the ticket being
        # actioned and closed
        final_status = "closed"

    return {"status": final_status}


# ---------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------


def get_triage_graph() -> StateGraph:
    """
    Build, compile, and return the TriageFlow LangGraph. This is the
    ONLY place the graph gets constructed.
    """
    builder = StateGraph(TicketState)

    builder.add_node("ingest", ingest_node)
    builder.add_node("classify", classify_node)
    builder.add_node("safety_check", safety_check_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("check_inventory", check_inventory_node)
    builder.add_node("draft", draft_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "classify")
    builder.add_edge("classify", "safety_check")
    builder.add_edge("safety_check", "retrieve")
    builder.add_edge("retrieve", "check_inventory")
    builder.add_edge("check_inventory", "draft")
    builder.add_edge("draft", "human_review")
    builder.add_edge("human_review", "finalize")
    builder.add_edge("finalize", END)

    # Replace with:
    conn = sqlite3.connect("./data/triageflow_checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    graph = builder.compile(checkpointer=checkpointer)

    return graph


if __name__ == "__main__":
    from backend.graphs.state import create_initial_state

    graph = get_triage_graph()
    config = {"configurable": {"thread_id": "test-1"}}

    initial_state = create_initial_state(
        "Pump P-204 making loud noise, vibration increasing since yesterday."
    )

    print("--- Running graph until it pauses at human_review ---")
    result = graph.invoke(initial_state, config=config)
    print("Paused state:", result)
    print()

    print("--- Resuming with a fake human decision ---")
    resumed = graph.invoke(
        Command(resume={"decision": "approve", "feedback": None}),
        config=config,
    )
    print("Final state:", resumed)


# # command parameter

# Command(
#     graph=None,
#     update=None,
#     resume=None,
#     goto=()
# )
