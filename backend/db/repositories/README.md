# backend/db/repositories/

## Purpose
This folder is where DATABASE QUERY LOGIC should live, separate from
both the model definitions (models.py) and the route handlers
(backend/api/routes/). This is the "Repository Pattern" — a thin layer
between your business logic and raw SQLAlchemy queries.

## Why bother with this layer?
Without it, query logic tends to get copy-pasted across multiple
route handlers, or worse, scattered into agent code. A repository
gives you one place per entity (e.g. `ticket_repository.py`) with
functions like `get_ticket_by_id()`, `list_tickets_by_status()`,
`create_ticket()` — your routes call these, they never write raw
SQLAlchemy queries themselves.

## TODO
Create files here as you need them, e.g.:
- `ticket_repository.py` — CRUD operations for the Ticket model
- `audit_repository.py` — append-only writes + queries for AuditLog

## Suggested approach
Don't build this layer speculatively before you need it. Build your
first API route, notice you're writing a raw query inline, and THEN
extract it into a repository function here. That's a more honest way
to learn when this pattern actually earns its keep versus being
premature abstraction.

## Learning objective
Understand the tradeoff between "just query the DB inline, it's
simpler" and "extract a repository layer, it's more testable/reusable"
— there's no universally correct answer, but you should be able to
explain your choice.
