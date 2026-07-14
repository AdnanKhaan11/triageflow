# backend/db/schemas/

## Purpose
Pydantic schemas for data validation at boundaries — specifically, the
shapes of data going INTO and OUT OF your API (as opposed to
models.py, which defines database TABLE structure). These are often
called "DTOs" (Data Transfer Objects) in other ecosystems.

## Why is this different from backend/db/models.py?
`models.py` = how data is STORED (SQLAlchemy ORM models, tied to table
structure).
`backend/db/schemas/` = how data looks when it crosses an API boundary
(Pydantic models, used for request/response validation in FastAPI).

These often look SIMILAR but serving different purposes. For example,
your API response for a ticket probably shouldn't expose every
internal database column — a schema lets you control that
deliberately instead of accidentally leaking internal fields.

## TODO
Create Pydantic models here matching the API request/response
examples in triageFlow_plan.md section 13, e.g.:
- `TicketCreateRequest` (matches the POST /tickets request body)
- `TicketResponse` (matches the ticket status response shape)
- `HumanDecisionRequest` (matches the POST /tickets/{id}/decision body)

## Learning objective
Understand why separating "storage shape" from "API shape" is good
practice, even when they look almost identical at this project's
small scale — the value shows up as the project grows and they
diverge.
