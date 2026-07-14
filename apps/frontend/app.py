"""
apps/frontend/app.py

RESPONSIBILITY
---------------
The Streamlit app entrypoint. Sets up page config and navigation
between the two main pages (Submit Ticket, Review Queue) described in
triageFlow_plan.md's user journey (section 7).

TODO
-----
1. Set Streamlit page config (title, layout).
2. Build simple navigation between pages — either Streamlit's native
   multipage app structure (files in `pages/` get auto-discovered) or
   a manual sidebar radio/selectbox switching between views. Streamlit
   has changed its multipage conventions across versions — check
   current docs for `st.navigation` / `st.Page` (newer) vs. the older
   `pages/` folder auto-discovery convention.
3. Initialize any app-wide session state defaults (see
   apps/frontend/utils/session_state.py).

HINTS
------
- Keep this file thin — actual page content belongs in
  apps/frontend/pages/, actual reusable UI pieces belong in
  apps/frontend/components/.
- This UI needs to call your FastAPI backend (not your LangGraph code
  directly) — see apps/frontend/utils/api_client.py.

LEARNING RESOURCES
--------------------
- Streamlit docs: "Multipage apps"

COMMON MISTAKES
-----------------
- Importing backend/ modules (agents, graph) directly into the
  Streamlit app instead of calling the FastAPI API. Keep frontend and
  backend genuinely decoupled — talk over HTTP, not via shared Python
  imports. This also matches how triageFlow_plan.md's architecture
  diagram (section 8) is drawn: UI -> API -> Graph, not UI -> Graph
  directly.
"""

from __future__ import annotations

# TODO: import streamlit as st
# TODO: implement per docstring steps 1-3 above
