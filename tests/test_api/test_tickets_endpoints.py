"""
tests/test_api/test_tickets_endpoints.py

WHAT TO TEST HERE
--------------------
End-to-end-ish tests of your FastAPI routes using FastAPI's
TestClient — these exercise the full stack (API -> graph -> database)
but stay within a single test process (no real network calls).

SUGGESTED TEST CASES
------------------------
1. POST /tickets with a valid raw_text -> 200/201 response with a
   ticket_id.
2. GET /tickets/{ticket_id} for a ticket that was just created ->
   returns the expected shape, status reflects where it is in the
   workflow.
3. GET /tickets?status=awaiting_review -> returns a list, and a
   freshly-created ticket should eventually show up here once it's
   reached the human_review pause point.
4. POST /tickets/{ticket_id}/decision with "approve" -> ticket status
   becomes "closed" when re-fetched.
5. GET /tickets/{nonexistent_id} -> proper 404, not a 500 crash.

SETUP NOTE
------------
Use a separate TEST database (e.g. an in-memory or temporary SQLite
file) — never run tests against whatever database you're using for
manual demo/development, or test runs will pollute your demo data.

LEARNING RESOURCES
--------------------
- FastAPI docs: "Testing" — covers TestClient and overriding
  dependencies (like swapping get_db for a test-database version).
"""

from __future__ import annotations

import pytest

# TODO: from fastapi.testclient import TestClient
# TODO: from backend.api.main import create_app


def test_create_ticket_returns_ticket_id():
    """TODO: implement test case 1 from the docstring above."""
    pytest.skip("Not implemented yet")


def test_get_nonexistent_ticket_returns_404():
    """TODO: implement test case 5 from the docstring above."""
    pytest.skip("Not implemented yet")
