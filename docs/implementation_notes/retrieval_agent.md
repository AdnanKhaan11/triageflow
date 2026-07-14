# Retrieval Agent — Implementation Notes

## Responsibilities
- Query the vector store for manual/SOP content relevant to a
  given ticket.
- Return chunks WITH their source metadata, so recommendations
  can be traced back to a specific manual section.

## Inputs
- The ticket's raw text and/or its classification fields.

## Outputs
- A list of `{text, source, section}` chunks, ranked by relevance.

## Suggested Approach
1. Get `vector_store.py` working and tested in isolation FIRST.
2. Decide what query text to use — raw ticket text vs. a
   reformulated query built from classification fields. Try both.
3. Start with top_k=3-5, tune based on observed quality.

## Common Mistakes
- Debugging a 'bad draft' when the actual root cause is poor
  retrieval three steps upstream — always sanity-check retrieval
  output independently first.
- Chunks too large or too small — both hurt relevance in different
  ways (see vector_store.py notes).

## Debugging Tips
- Print retrieved chunks (and similarity scores, if exposed) for
  every test query during development — never fly blind into the
  drafting step.

## Learning Objectives
- Understand the practical impact of chunking strategy on RAG
  quality.
- Understand why 'input quality and chunking matter more than
  vector DB choice' (a well-established finding as of 2026 RAG
  practice).

---
*This is a guidance document only. No implementation code lives here —
see the corresponding source file's docstring for the actual TODO list.*
