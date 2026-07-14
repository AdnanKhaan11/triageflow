# Safety Rules — Implementation Notes

## Responsibilities
- Apply deterministic, hard-coded urgency overrides that do NOT
  depend on LLM judgment, for safety-critical keywords.

## Inputs
- `raw_text: str`, `classification: dict`.

## Outputs
- A (possibly modified) classification dict, plus a flag indicating
  whether an override was applied.

## Suggested Approach
1. Define a short, easily-extendable list of trigger phrases.
2. Keep matching simple (case-insensitive substring) — deliberately,
   not cleverly.
3. Make sure the override flag is surfaced all the way to the UI.

## Common Mistakes
- Putting this logic inside the LLM prompt instead of as
  independent, deterministic post-processing — defeats the purpose
  of a guardrail that doesn't depend on LLM compliance.

## Debugging Tips
- N/A — this is intentionally simple, deterministic logic; if it's
  not working, the bug is almost certainly a typo in the trigger
  list or a missed integration point, not a subtle logic error.

## Learning Objectives
- Understand WHY production agentic systems separate deterministic
  safety guardrails from LLM judgment — this is the single most
  interview-relevant architectural lesson in this whole project.

---
*This is a guidance document only. No implementation code lives here —
see the corresponding source file's docstring for the actual TODO list.*
