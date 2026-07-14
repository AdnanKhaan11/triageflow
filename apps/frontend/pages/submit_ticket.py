"""
apps/frontend/pages/submit_ticket.py

RESPONSIBILITY
---------------
The "submit a new ticket" page — a simple form matching Persona 2
(Amara, Field Technician) from triageFlow_plan.md section 6: she wants
a FAST, simple way to report a problem.

TODO
-----
1. A text area for the raw ticket description.
2. A submit button that calls your API client's create_ticket()
   function (see apps/frontend/utils/api_client.py).
3. Show a confirmation with the returned ticket_id after submission.
4. Consider: should the user see a loading spinner while the backend
   processes the ticket through classification/retrieval/drafting?
   (Likely yes — triageFlow_plan.md's NFR table targets under 15
   seconds end-to-end, which is long enough that a spinner matters for
   perceived responsiveness.)

HINTS
------
- Use `st.spinner("Processing ticket...")` around the API call.
- Keep the form itself minimal — Amara's persona explicitly doesn't
  want a long form.

LEARNING RESOURCES
--------------------
- Streamlit docs: "st.form", "st.spinner"
"""

from __future__ import annotations

# TODO: implement per docstring steps 1-4 above
