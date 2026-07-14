# docs/architecture/

## Purpose
Keep your ACTUAL architecture diagrams here as you build — not just
the planned ones from triageFlow_plan.md. It's normal and expected for
the real implementation to diverge slightly from the plan (e.g. you
decide to merge two agents, or add a node you didn't originally
think of).

## TODO
1. As you build, export/update Mermaid diagrams reflecting what you
   ACTUALLY built (use `graph.get_graph().draw_mermaid()` on your
   compiled LangGraph for the workflow diagram — don't hand-draw it
   from memory, generate it from the real code).
2. Note any deliberate deviations from the original plan doc and WHY
   — this kind of "as-built vs. as-planned" documentation is exactly
   what real engineering teams maintain, and it's a great thing to
   walk an interviewer through.
