"""
apps/frontend/utils/session_state.py

RESPONSIBILITY
---------------
Helpers for initializing and accessing Streamlit's `st.session_state`
consistently across pages — e.g. tracking which ticket is currently
selected for review.

WHY THIS FILE EXISTS
------------------------
Streamlit reruns your ENTIRE script top-to-bottom on every interaction
— `st.session_state` is how you persist anything across those reruns
(like "which ticket did the user click on"). Centralizing the default
keys/values here (instead of scattering
`if "x" not in st.session_state: ...` checks across every page) keeps
this consistent and easy to extend.

TODO
-----
1. A function `init_session_state() -> None` that sets sensible
   defaults for any keys your pages rely on (e.g.
   `selected_ticket_id`, defaulting to None) — call this once from
   apps/frontend/app.py at startup.

HINTS
------
- Look up Streamlit's `st.session_state` docs if this pattern (state
  persisting across reruns of the whole script) is new to you — it's
  one of the more unusual things about Streamlit compared to typical
  web frameworks.

LEARNING RESOURCES
--------------------
- Streamlit docs: "Session State"
"""

from __future__ import annotations


def init_session_state() -> None:
    """
    TODO: See module docstring step 1 above.
    """
    raise NotImplementedError("Implement init_session_state")
