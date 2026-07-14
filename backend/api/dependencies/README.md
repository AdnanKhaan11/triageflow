# backend/api/dependencies/

## Purpose (placeholder folder)
FastAPI "Depends()"-style shared dependencies that don't belong to one
specific route file — e.g. authentication checks, pagination
parameter parsing, or a shared rate-limiter.

## Why this is mostly empty for MVP
triageFlow_plan.md section 3 explicitly puts authentication/multi-user
out of scope for MVP. The main dependency this project actually needs
right now (`get_db` for database sessions) already lives in
backend/db/session.py and is imported directly into routes — that's
fine at this scale.

## TODO (only if you add scope later)
If you implement any V2 features from triageFlow_plan.md section 23
(e.g. role-based access), this is where a shared
`get_current_user()`-style dependency would go.
