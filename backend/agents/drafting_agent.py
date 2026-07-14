"""
backend/agents/drafting_agent.py

Generates a grounded, citation-backed maintenance recommendation from
classification + retrieved manual chunks + inventory status.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from backend.services.llm_client import get_chat_model

DRAFT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a Senior Industrial Maintenance Engineer with more than 20 years of experience in equipment troubleshooting, maintenance planning, and Standard Operating Procedures (SOPs).

Your responsibility is to generate a professional maintenance recommendation based ONLY on the provided information.

##############################
## PRIMARY OBJECTIVE
##############################

Generate a clear, practical, and safety-focused maintenance recommendation that can be reviewed by a human maintenance supervisor.

Your response MUST be grounded entirely in the provided manual excerpts.

Never use outside knowledge.
Never invent procedures.
Never guess missing information.

If the retrieved context is insufficient, explicitly state that additional manual review is required.

##############################
## SAFETY RULES
##############################

Safety has the highest priority.

If information is missing, DO NOT hallucinate. Instead write:
"Insufficient information found in the retrieved maintenance manual. Manual review is recommended."

Never fabricate:
- Procedures
- Torque values
- Operating limits
- Inspection intervals
- Safety precautions
- Replacement procedures

##############################
## HOW TO USE THE CONTEXT
##############################

Use ONLY:
1. Ticket Classification
2. Retrieved Manual Chunks
3. Inventory Information

Do NOT rely on your own knowledge. Every maintenance recommendation
should be supported by the retrieved documentation.

##############################
## CITATION RULES
##############################

Whenever you use information from the manual, cite the source.
Example: (Source: TriageFlow_Equipment_Manual.pdf, Page 12)

Every recommendation should have a citation whenever possible.

##############################
## INVENTORY RULES
##############################

Consider inventory before recommending replacement.
If required parts are unavailable, mention the estimated lead time.
Do NOT recommend immediate replacement if inventory indicates the
part is unavailable.

##############################
## WRITING STYLE
##############################

Sound like a professional maintenance engineer. Avoid AI-style
wording. Avoid unnecessary explanations. Use short, actionable
sentences. Be specific. Be practical.

##############################
## OUTPUT FORMAT
##############################

Return your answer in exactly this structure.

### Equipment
...
---
### Fault Classification
...
---
### Priority
...
---
### Diagnosis
...
---
### Recommended Actions
1.
2.
3.
4.
---
### Required Spare Parts
...
---
### Inventory Status
...
---
### Safety Notes
...
---
### Escalation Recommendation
...
---
### Supporting Manual References
-
-
---
### Confidence
High / Medium / Low

Confidence should be LOW if insufficient manual context exists.
Never output anything outside this structure.
""",
        ),
        (
            "human",
            """
Generate the maintenance recommendation using the information below.

=============================
Ticket Classification
=============================
Equipment ID: {equipment_id}
Fault Type: {fault_type}
Priority: {priority}

Original Ticket:
{raw_ticket}

=============================
Retrieved Manual Chunks
=============================
{retrieved_chunks}

=============================
Inventory Result
=============================
Parts Available: {parts_available}
Estimated Lead Time: {eta_days}

=============================
Instructions
=============================
- Use ONLY the retrieved manual.
- Never invent maintenance procedures.
- Never fabricate safety information.
- Cite the manual source whenever possible.
- Mention inventory implications.
- If information is missing, clearly state that manual review is required.

Begin your response now.
""",
        ),
    ]
)


def build_draft_prompt(state: dict):
    """
    Convert state into a formatted prompt value. No LLM calls here —
    just builds the prompt object to be sent to the LLM client later.
    """
    retrieved_chunks = state.get("retrieved_chunks", [])

    if retrieved_chunks:
        chunks_text = "\n\n".join(
            f"Source: {chunk['source']}, Page: {chunk.get('page', 'N/A')}\n{chunk['text']}"
            for chunk in retrieved_chunks
        )
    else:
        # Explicit empty-retrieval case -- per the scaffold's hint,
        # we tell the LLM directly rather than leaving it to guess.
        chunks_text = "No relevant manual content was retrieved for this ticket."

    classification = state.get("classification", {})
    inventory_check = state.get("inventory_check", {})

    return DRAFT_PROMPT.format_prompt(  # .format_prompt() we can put the values into the prompt template, and it will return a PromptValue object that can be sent to the LLM client.
        equipment_id=classification.get("equipment_id", "Unknown"),
        fault_type=classification.get("fault_type", "Unknown"),
        priority=classification.get("urgency", "Unknown"),
        raw_ticket=state.get("raw_text", ""),
        retrieved_chunks=chunks_text,
        parts_available=inventory_check.get("parts_available", "Unknown"),
        eta_days=inventory_check.get("eta_days", "Unknown"),
    )


def generate_recommendation(prompt) -> str:
    """
    Sends the already-built prompt to the LLM and returns the raw
    text recommendation.
    """
    llm = get_chat_model()
    response = llm.invoke(
        prompt.to_messages()
    )  # .to_messages() converts the prompt to the format expected by the LLM client e.g HumanMessage, SystemMessage, etc. depending on the LLM client implementation.
    return response.content


def draft_node(state: dict) -> dict:
    """
    Reads classification, retrieved_chunks, and inventory_check from
    state, and returns a partial update with 'draft_recommendation'
    populated.
    """
    prompt = build_draft_prompt(state)

    last_error = None
    for attempt in range(2):
        try:
            recommendation = generate_recommendation(prompt)
            return {"draft_recommendation": recommendation}
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt + 1} failed: {e}")

    return {
        "draft_recommendation": None,
        "manual_review_required": True,
        "error": str(last_error),
    }


if __name__ == "__main__":
    test_state = {
        "raw_text": "Pump P-204 making loud noise, vibration increasing since yesterday.",
        "classification": {
            "equipment_id": "P-204",
            "fault_type": "vibration",
            "urgency": "medium",
            "confidence": 0.85,
        },
        "retrieved_chunks": [
            {
                "source": "TriageFlow_Equipment_Manual.pdf",
                "page": 4,
                "text": "1.2.2 Troubleshooting Procedure - Vibration Increase: "
                "Confirm vibration reading against baseline...",
            }
        ],
        "inventory_check": {"parts_available": True, "eta_days": 2},
    }

    result = draft_node(test_state)
    print(result["draft_recommendation"])
