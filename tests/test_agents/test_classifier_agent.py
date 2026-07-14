"""
tests/test_agents/test_classifier_agent.py

WHAT TO TEST HERE
--------------------
Unit tests for classify_node in isolation — NOT through the full
graph, NOT through the API. Just: given raw ticket text, does the
classifier produce a reasonable, schema-valid output?

SUGGESTED TEST CASES (write these as you implement the agent)
-------------------------------------------------------------------
1. A clearly low-urgency ticket (e.g. "small dent in equipment
   casing, purely cosmetic") -> expect urgency in {"low", "medium"}.
2. A clearly critical ticket (e.g. "gas leak detected near unit 7")
   -> expect urgency == "critical" — NOTE: this might be the safety
   override layer's job, not the classifier's; decide whether this
   test belongs here or in test_safety_rules.py and be deliberate
   about it.
3. An AMBIGUOUS ticket where reasonable humans might disagree on
   urgency — this is the interesting test. What does your classifier
   actually do? Does it report a lower confidence score? This is
   exactly the scenario triageFlow_plan.md's risk assessment (section
   17) flags as the top AI risk.
4. Malformed/garbage input (empty string, random characters) — does
   the agent fail gracefully or crash?
5. Schema validation: does the output always match your Pydantic
   TicketClassification model, across all the above cases?

TESTING STRATEGY NOTE
------------------------
Since this agent calls a real LLM, you have two options:
  (a) Use real API calls in tests (costs a few cents per test run,
      but tests REAL behavior — recommended given this project's
      near-zero cost budget, see triageFlow_plan.md section 21).
  (b) Mock the LLM client and test only the surrounding logic (retry,
      error handling) — faster/free, but doesn't catch real prompt
      quality issues.
A reasonable approach: a SMALL number of real-API tests (the 5 cases
above) for prompt-quality confidence, plus mocked tests for error
handling paths you don't want to pay to trigger repeatedly.

LEARNING RESOURCES
--------------------
- pytest docs: "Fixtures", "Parametrize" (parametrize is a clean way
  to run the same test logic across multiple ticket-text inputs)
"""

from __future__ import annotations

import pytest

# TODO: from backend.agents.classifier_agent import classify_node


def test_low_urgency_ticket_classified_correctly():
    """TODO: implement test case 1 from the docstring above."""
    pytest.skip("Not implemented yet")


def test_critical_keyword_ticket():
    """TODO: implement test case 2 from the docstring above."""
    pytest.skip("Not implemented yet")


def test_ambiguous_ticket_has_lower_confidence():
    """TODO: implement test case 3 from the docstring above."""
    pytest.skip("Not implemented yet")


def test_malformed_input_does_not_crash():
    """TODO: implement test case 4 from the docstring above."""
    pytest.skip("Not implemented yet")
