# data/manuals/

## Purpose
This is where your SYNTHETIC equipment manuals / SOPs live — the
source documents that get ingested into the vector store (see
backend/services/vector_store.py).

## TODO (this is content-creation work, not coding)
Per triageFlow_plan.md Phase 1 of the roadmap (section 16): create
roughly 10-15 short synthetic manual documents covering a handful of
fictional equipment IDs (e.g. P-204, C-310, V-118) and common fault
types (vibration, overheating, leak, electrical fault).

Tips:
- You can use an LLM to help DRAFT these quickly, but read through
  each one — you'll be relying on their content to judge whether your
  retrieval and drafting agents are working correctly, so you need to
  actually know what's in them.
- Give each document clear section headings/numbers (e.g. "4.3 Bearing
  Inspection Procedure") — this lets your retrieval agent's citations
  be meaningful (see drafting_agent.md implementation notes).
- Deliberately include a FEW documents with overlapping/similar
  content for different equipment, so you have a real test of whether
  retrieval picks the RIGHT one, not just A relevant one.

Format: plain `.txt` or `.md` files are simplest to start ingesting
quickly; you can move to PDF later if you want to also practice PDF
text extraction.
