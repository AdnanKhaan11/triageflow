# backend/api/schemas/

## Purpose
NOTE: there are two "schemas" folders in this project
(backend/api/schemas/ AND backend/db/schemas/) — this is deliberate,
but make sure you understand WHY, don't just copy-paste between them.

- `backend/db/schemas/` = Pydantic models for data crossing the
  DATABASE boundary conceptually (what a "Ticket" looks like as data).
- `backend/api/schemas/` = Pydantic models SPECIFIC to API
  request/response shapes that might not map 1:1 to a database entity
  at all (e.g. a paginated list response wrapper, an error response
  shape).

If this distinction feels redundant at this project's scale, you're
not wrong — for a project this size you could merge them into one
folder. Keeping them separate here is meant to show you the PATTERN
used in larger production codebases, where the distinction earns its
keep. Feel free to consciously simplify this if you decide the
separation isn't pulling its weight for a project this size — and be
ready to explain that decision, that's a legitimate architectural
judgment call.

## TODO
Add schemas here as you discover you need API-shape-specific models
that don't belong in db/schemas/.
