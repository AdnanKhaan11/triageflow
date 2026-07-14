# Classifier Agent — Implementation Notes

## Responsibilities
- Extract structured fields from free-text maintenance tickets.
- Assign an urgency level the rest of the system will act on.
- Report a confidence score so downstream consumers (and the human
  reviewer) can judge how much to trust the classification.

## Inputs
- `raw_text: str` — the technician's free-text ticket description.

## Outputs
- A structured object: `{equipment_id, fault_type, urgency, confidence}`.

## Suggested Approach
1. Define the output schema as a Pydantic model first.
2. Use your LLM client's native structured-output feature — don't
   hand-parse JSON from free text.
3. Write and iterate on the prompt using ~10 hand-written test
   tickets, including deliberately ambiguous ones.
4. Add retry logic for API failures (max 2 attempts, per the plan doc).

## Common Mistakes
- Parsing JSON out of free-form LLM text instead of using structured
  output / tool calling.
- Letting this agent also apply safety-critical overrides — that
  logic belongs in `safety_rules.py`, not here. Keep this agent's
  responsibility narrow.

## Debugging Tips
- Print the raw model response before any parsing if structured
  output validation keeps failing.
- Keep a fixed set of test tickets you re-run every time you change
  the prompt, so you can see what changed and what broke.

## Learning Objectives
- Understand structured output / tool-calling APIs for reliable
  extraction.
- Understand why confidence scores matter in a human-in-the-loop
  system.

---
*This is a guidance document only. No implementation code lives here —
see the corresponding source file's docstring for the actual TODO list.*
