# TriageFlow

> An agentic AI system that classifies, investigates, and drafts action
> plans for industrial maintenance tickets — with mandatory human
> approval before any action is taken.

## Status

🚧 **This is a scaffold, not a finished project.** Every file in this
repository contains a docstring explaining its responsibility, plus
TODOs, hints, and learning resources — but the actual implementation
logic has been deliberately left out so it can be built (and learned)
by hand.

See `triageFlow_plan.md` for the full architecture and planning
document this scaffold was generated from.

## Getting Started

1. Copy `.env.example` to `.env` and fill in your LLM API key.
2. `pip install -r requirements.txt`
3. Start with `docs/implementation_notes/` — read the guide for
   whichever component you're about to implement before touching the
   code.
4. Suggested build order (matches `triageFlow_plan.md` section 16,
   Development Roadmap):
   - Phase 1: `data/manuals/`, `backend/services/vector_store.py`
   - Phase 2: `backend/agents/*` (one at a time, test each in
     isolation — see `tests/test_agents/`)
   - Phase 3: `backend/graphs/*` (wire it all together)
   - Phase 4: `backend/api/*`, `apps/frontend/*`
   - Phase 5: polish, deploy, write up what you learned in
     `docs/learning_path/`

## Project Structure

See `docs/architecture/` for diagrams, and `triageFlow_plan.md` section
15 for the original planned folder structure this scaffold implements.

## Why This Project Exists

Built as a portfolio project demonstrating production-style agentic AI
architecture: multi-step LangGraph orchestration, RAG-grounded
generation, deterministic safety guardrails, and human-in-the-loop
approval with full audit logging.

## License

TODO: pick a license if you intend to make this repository public.
