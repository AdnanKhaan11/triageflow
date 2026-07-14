# backend/db/migrations/

## Purpose (placeholder folder)
This folder is a placeholder for a real migration tool (Alembic is
the standard choice alongside SQLAlchemy) if/when you outgrow
`init_db()`'s simple `create_all()` approach.

## Why this is NOT set up yet
For this project's MVP scope (triageFlow_plan.md section 22), a single
`create_all()` call in `backend/db/session.py` is sufficient — there's
no existing production data to migrate carefully around yet. Setting
up Alembic now would be premature complexity.

## TODO (optional, stretch goal)
If you want the extra learning exercise:
1. `pip install alembic`
2. `alembic init backend/db/migrations`
3. Configure `alembic.ini` and `env.py` to point at your models'
   `Base.metadata`
4. Generate your first migration: `alembic revision --autogenerate`

## Learning objective
Understand WHEN a project actually needs a migration tool (answer:
once there's real data you can't just drop and recreate) versus when
`create_all()` is genuinely fine.
