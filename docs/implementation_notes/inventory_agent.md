# Inventory Agent — Implementation Notes

## Responsibilities
- Demonstrate tool-calling: looking up mocked spare-parts data
  given an equipment ID and fault type.

## Inputs
- `equipment_id: str`, `fault_type: str`.

## Outputs
- `{parts_available: bool, eta_days: int}`.

## Suggested Approach
1. Build a small static lookup table (dict or JSON file).
2. Decide: fixed graph step, or an LLM-invoked tool call? Both are
   defensible — have a reason for your choice.

## Common Mistakes
- Over-investing time in making mock data 'realistic' — this is
  explicitly out of scope detail per the plan doc.

## Debugging Tips
- N/A — this is deliberately simple, deterministic logic.

## Learning Objectives
- Understand the tool-calling pattern in agentic systems, even
  when the 'tool' itself is intentionally mocked.

---
*This is a guidance document only. No implementation code lives here —
see the corresponding source file's docstring for the actual TODO list.*
