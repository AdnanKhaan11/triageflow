"""
tests/test_e2e/test_full_ticket_lifecycle.py

WHAT TO TEST HERE
--------------------
The complete user journey from triageFlow_plan.md section 7, exercised
as one continuous test: submit -> classify -> retrieve -> draft ->
human review -> close. This is your "does the whole story actually
work" test — the one you'd run right before a demo to sanity-check
everything end-to-end.

SUGGESTED TEST CASE
-----------------------
1. Submit a realistic ticket via the API.
2. Poll/wait for it to reach "awaiting_review" status (with a
   reasonable timeout — don't let a flaky LLM response hang the test
   suite forever).
3. Fetch the ticket, assert classification + draft fields are
   populated and non-empty.
4. Submit an "approve" decision.
5. Fetch the ticket again, assert status is "closed".
6. Fetch the audit log, assert it contains an entry for every major
   step (ingest, classify, retrieve, draft, human_review, finalize).

WHY THIS TEST IS WORTH HAVING EVEN THOUGH IT'S SLOW/COSTS MONEY
---------------------------------------------------------------------
Unit tests can all pass while the pieces still don't fit together
correctly. This test is your insurance against that — and it's also,
practically, a great thing to have working and demonstrable before
walking into an interview where someone might ask "can you show me it
actually running end to end?"

LEARNING RESOURCES
--------------------
- This test doesn't need new library knowledge — it's mostly about
  composing what you already tested in test_api/ and test_graph/ into
  one continuous scenario.
"""

from __future__ import annotations

import pytest


def test_full_ticket_lifecycle():
    """TODO: implement the 6-step scenario from the docstring above."""
    pytest.skip("Not implemented yet")
