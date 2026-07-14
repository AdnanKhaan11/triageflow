"""
apps/frontend/pages/review_queue.py

RESPONSIBILITY
---------------
The human-in-the-loop review page — matches Persona 1 (Yusuf,
Maintenance Supervisor) from triageFlow_plan.md section 6. This is
arguably the most IMPORTANT page in the whole UI: it's where the
"human-in-the-loop" story becomes visible and real, not just an
architecture diagram claim.

TODO
-----
1. List tickets with status "awaiting_review" (call your API client's
   list_tickets(status="awaiting_review") function).
2. For a selected ticket, display:
   - The original raw ticket text
   - The classification (equipment, fault type, urgency) — and
     CLEARLY indicate if safety_override_applied is True, so the
     supervisor knows urgency was forced by a hard rule, not the AI's
     judgment (see backend/services/safety_rules.py notes — this
     traceability is the whole point of that file existing).
   - The retrieved manual sections it was based on (source citations —
     see backend/agents/drafting_agent.py notes on grounding)
   - The drafted recommendation
3. Three action buttons: Approve, Edit, Reject.
   - Edit should reveal a text area pre-filled with the draft,
     editable before submission.
   - Reject should reveal a text area for the rejection reason.
4. On any action, call your API client's submit_decision() function.

HINTS
------
- This page is where a recruiter/interviewer demo will likely spend
  the most time if you show this project live — make sure the safety
  override indicator and source citations are VISUALLY obvious, not
  buried in small text. This is the page that actually demonstrates
  the project's core thesis.

LEARNING RESOURCES
--------------------
- Streamlit docs: "st.button", "st.text_area", "st.columns" (useful
  for laying out the three action buttons side by side)

COMMON MISTAKES
-----------------
- Building this page to just show a flat block of text. Use
  Streamlit's layout primitives (columns, expanders, metrics) to make
  the classification, retrieval sources, and draft visually distinct
  sections — this materially affects how impressive the live demo
  feels.
"""

from __future__ import annotations

# TODO: implement per docstring steps 1-4 above
