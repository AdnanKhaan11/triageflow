# LangGraph Workflow — Implementation Notes

## Responsibilities
- Wire all agent nodes into a single StateGraph in the correct
  order.
- Implement the human-in-the-loop pause/resume at human_review.
- Attach a checkpointer so paused runs survive restarts.

## Inputs
- A `TicketState` (see state.py) at graph invocation time.

## Outputs
- A compiled, runnable LangGraph instance via `get_triage_graph()`.

## Suggested Approach
1. Get a LINEAR graph (no interrupt yet) working end-to-end first —
   prove the wiring before adding the hardest piece.
2. Add the checkpointer.
3. Add the human_review interrupt last, once everything else works.
4. Use `graph.get_graph().draw_mermaid()` to visually verify your
   actual compiled graph matches the plan doc's diagram.

## Common Mistakes
- Implementing human-in-the-loop with a custom while-loop instead of
  LangGraph's native `interrupt()` — defeats the purpose and won't
  survive a restart.
- Forgetting `thread_id` in the invocation config — resume will
  silently fail or start a new run instead.

## Debugging Tips
- `draw_mermaid()` to catch wiring mismatches.
- If interrupt isn't pausing, check first whether a checkpointer is
  actually attached at compile time.

## Learning Objectives
- Understand StateGraph construction, conditional/linear edges,
  checkpointing, and the interrupt/resume pattern — this is the
  single most important technical skill this whole project is
  meant to teach.

---
*This is a guidance document only. No implementation code lives here —
see the corresponding source file's docstring for the actual TODO list.*
