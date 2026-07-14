"""
tests/test_agents/test_retrieval_agent.py

WHAT TO TEST HERE
--------------------
Whether retrieve_node returns sensible chunks for known queries —
this requires your test vector store to actually be populated with
some known documents first.

SUGGESTED TEST CASES
------------------------
1. A query that clearly matches one of your ingested manual
   documents -> the top retrieved chunk should be FROM that document
   (check the source metadata, not just that something came back).
2. A query about equipment that has NO matching manual -> what
   happens? Does retrieval return low-relevance chunks anyway, or can
   you detect "nothing good matched" and signal that downstream (see
   drafting_agent.py notes on handling empty/poor retrieval)?
3. Top-k behavior: does requesting top_k=3 actually return at most 3
   results?

SETUP NOTE
------------
You'll likely want a small, FIXED test document set (separate from
your "real" demo manuals) ingested into a TEST vector store collection
specifically for these tests, so test results don't depend on however
your demo data happens to be set up that day. Consider a pytest
fixture that ingests a tiny known document into a temporary Chroma
collection before each test.

LEARNING RESOURCES
--------------------
- pytest docs: "Fixtures" (for the temporary test vector store setup)
"""

from __future__ import annotations

import pytest

# TODO: from backend.agents.retrieval_agent import retrieve_node


def test_retrieval_returns_relevant_source():
    """TODO: implement test case 1 from the docstring above."""
    pytest.skip("Not implemented yet")


def test_retrieval_respects_top_k():
    """TODO: implement test case 3 from the docstring above."""
    pytest.skip("Not implemented yet")
