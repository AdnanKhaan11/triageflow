"""
backend/db/session.py

Database connection/session management.
"""

from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.models import Base

# Read from environment variable, fall back to local SQLite file.
# For SQLite: "sqlite:///./triageflow.db"
# For Postgres: "postgresql://user:password@localhost/triageflow"
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./triageflow.db")

# check_same_thread is SQLite-specific — required because FastAPI
# handles requests across multiple threads, but SQLite by default
# only allows the thread that created the connection to use it.
# Setting this to False disables that restriction safely.
# Postgres doesn't need this argument at all.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# The engine is the actual connection to the database.
# Created once, reused for every request.
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# SessionLocal is a factory that produces fresh database sessions.
# autocommit=False means changes don't save automatically —
# you must call db.commit() explicitly, which gives you control
# over when data actually gets written.
# autoflush=False means SQLAlchemy won't auto-sync pending changes
# before every query — you control this manually too.
# in simple term session is a temporary workspace(it means a temporary
#  area where you can work with the database) for 
# interacting with the database. It allows you to query, 
# add, update, and delete records in a controlled manner. 
# Once you're done with your operations, you can commit the changes 
# to make them permanent or roll them back if something goes wrong.

SessionLocal = sessionmaker(
    bind=engine, # bind = engine means every session uses this engine 
    autocommit=False, # it means changes don't save automatically — you must call db.commit()(db.commit() means you have to explicitly commit the changes) explicitly, which gives you control over when data actually gets written.
    autoflush=False, # it means SQLAlchemy won't auto-sync (auto-sync means in simple terms is the process of synchronizing(synchronizing meaning is ) data between different sources) pending changes before every query — you control this manually too.
)


def get_db():
    """
    FastAPI dependency that yields a database session per request,
    then always closes it when the request is done — even if an
    exception occurred.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db # yield is used to produce a value from a generator function
    finally:
        db.close()


def init_db() -> None:
    """
    Creates all tables defined in models.py if they don't exist yet.
    Call this once on app startup (see backend/api/main.py).

    This is fine for development. For production with real data,
    you'd use Alembic migrations instead of create_all().
    """
    Base.metadata.create_all(bind=engine) # this line creates all tables defined in models.py if they don't exist yet. It uses the metadata of the Base class to create the tables in the database. The bind=engine argument specifies which database engine to use for creating the tables.


if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print(f"Done. Database file: {DATABASE_URL}")