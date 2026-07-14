# docs/decisions/

## Purpose
A lightweight "Architecture Decision Records" (ADR) log. Every time
you make a non-trivial decision (e.g. "TypedDict vs Pydantic for
state," "ChromaDB vs Qdrant," "synchronous vs background-task ticket
processing"), write a short note here.

## Suggested format per decision (keep it SHORT — a paragraph or two)

    # ADR-001: <short title>

    ## Context
    What problem/choice were you facing?

    ## Decision
    What did you choose?

    ## Why
    What made you choose it over the alternative(s)?

    ## Tradeoffs accepted
    What did you give up by choosing this?

## Why this matters for your hiring goal
This is one of the highest-leverage files in the whole repo for
interview purposes. "Walk me through a technical decision you made
and why" is an extremely common interview question — having real,
written decisions (made WHILE building, not reconstructed afterward
from memory) is far more convincing than trying to recall your
reasoning live under interview pressure.

## TODO
Create one markdown file per significant decision as you make it,
e.g. `001-state-schema-typeddict-vs-pydantic.md`,
`002-vector-db-choice.md`, etc.
