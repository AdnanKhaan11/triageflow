from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from backend.services.llm_client import get_chat_model
from langchain_core.prompts import ChatPromptTemplate

"""
backend/agents/classifier_agent.py

RESPONSIBILITY (from triageFlow_plan.md section 10)
-------------------------------------------------------
    Purpose: Extract structured data + urgency from free text
    Inputs:  Raw ticket text
    Outputs: {equipment_id, fault_type, urgency, confidence}
    Tools:   LLM (structured output / JSON mode)

WHY THIS AGENT IS HARDER THAN IT LOOKS
------------------------------------------
"Just ask the LLM to extract some fields" sounds trivial, but getting
RELIABLE structured output (not "usually valid JSON, sometimes a
markdown code block, sometimes a friendly sentence first") is the real
skill here. This is exactly the kind of detail that separates a
"prompt and hope" project from a production-credible one.
"""


"""
backend/agents/classifier_agent.py

Extracts structured data (equipment, fault type, urgency, confidence)
from a raw maintenance ticket using an LLM with structured output.
"""


class TicketClassification(BaseModel):
    equipment_id: str
    fault_type: str
    urgency: Literal["low", "medium", "high", "critical"]
    confidence: float


llm = get_chat_model()
structured_llm = llm.with_structured_output(TicketClassification)


def classify_node(state: dict) -> dict:
    """
    Reads state['raw_text'], classifies it, returns a partial state
    update with 'classification' populated.
    """
    raw_text = state["raw_text"]

    prompt = ChatPromptTemplate.from_template(
        """ You are a maintenance ticket classification assistant.

                  Your task is to analyze a maintenance ticket and extract:

                  1. equipment_id
                  2. fault_type
                  3. urgency
                  4. confidence

                  Urgency Definitions:

                  LOW

                  * Minor issue
                  * No immediate operational impact
                  * Can be scheduled later

                  MEDIUM

                  * Equipment performance degraded
                  * Issue should be addressed soon
                  * Not immediately disrupting operations

                  HIGH

                  * Equipment malfunctioning
                  * Operations impacted
                  * Risk of further damage if not addressed

                  CRITICAL

                  * Complete equipment failure
                  * Immediate safety concern
                  * Immediate production impact
                  * Emergency situation

                  IMPORTANT:

                  * Only classify based on information present in the ticket.
                  * Do not invent missing information.
                  * Do not apply safety override rules.
                  * Safety override rules are handled by a separate system.
                  * If information is unclear, lower confidence appropriately.
                  * Confidence must be between 0.0 and 1.0.

                  Examples:

                  Ticket:
                  "Pump P-204 making loud vibration and noise."

                  Classification:
                  equipment_id = P-204
                  fault_type = vibration
                  urgency = medium
                  confidence = 0.82

                  Ticket:
                  "Compressor C-11 has stopped operating and production is halted."

                  Classification:
                  equipment_id = C-11
                  fault_type = compressor failure
                  urgency = critical
                  confidence = 0.95

                  Ticket:
                  "Motor M-18 temperature slightly higher than normal."

                  Classification:
                  equipment_id = M-18
                  fault_type = overheating
                  urgency = low
                  confidence = 0.75

                  Ticket:
                  {raw_text}
                   """
    )

    formatted_prompt = prompt.format_prompt(raw_text=raw_text)

    last_error = None
    for attempt in range(2):
        try:
            result = structured_llm.invoke(formatted_prompt)
            return {"classification": result.model_dump()}
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt + 1} failed: {e}")

    return {
        "classification": None,
        "manual_review_required": True,
        "error": str(last_error),
    }


if __name__ == "__main__":
    test_state = {
        "raw_text": "Pump P-204 making loud noise, vibration increasing since yesterday."
    }
    print(classify_node(test_state))
