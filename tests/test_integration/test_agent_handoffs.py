"""
tests/test_integration/test_agent_handoffs.py

WHAT TO TEST HERE
--------------------
The HANDOFFS between agents — does the output of one agent actually
work as valid input to the next, independent of running the full
graph? This sits between unit tests (one agent in isolation) and
graph tests (the whole wired-up workflow).

SUGGESTED TEST CASES
------------------------
1. Take a real classify_node() output, feed it directly into
   retrieve_node() — does retrieval actually use the classification
   fields sensibly (see retrieval_agent.py notes on query
   reformulation)?
2. Take real retrieve_node() output (including an EMPTY result list)
   and feed it into draft_node() — does the drafting agent handle the
   "nothing relevant was found" case the way you intended (see
   drafting_agent.py notes on this exact scenario)?
3. Take a classification BEFORE and AFTER apply_safety_override() — do
   downstream agents (retrieval, drafting) behave correctly with the
   overridden urgency value?

WHY THIS LAYER IS WORTH HAVING SEPARATELY FROM test_agents/
-----------------------------------------------------------------
Unit tests in test_agents/ test each agent against hand-crafted inputs
you imagined. These integration tests use REAL outputs from one agent
as input to the next, which catches the bugs that only show up at the
seams — e.g. a field name mismatch between what classify_node returns
and what retrieve_node expects to read.

LEARNING RESOURCES
--------------------
- No new library knowledge needed — this is about test SCOPE/strategy,
  not new tools.
"""

from __future__ import annotations

import pytest


def test_classification_to_retrieval_handoff():
    """TODO: implement test case 1 from the docstring above."""
    pytest.skip("Not implemented yet")


def test_empty_retrieval_to_drafting_handoff():
    """TODO: implement test case 2 from the docstring above."""
    pytest.skip("Not implemented yet")
