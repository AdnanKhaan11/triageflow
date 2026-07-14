"""
backend/api/main.py

FastAPI application entrypoint.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import tickets as tickets_router
from backend.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Splits app lifecycle into startup (before yield) and shutdown
    (after yield). FastAPI runs the application in between.
    """
    print("Starting TriageFlow API...")
    init_db()
    yield
    print("Shutting down TriageFlow API...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="TriageFlow API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5500",  # frontend
            "http://127.0.0.1:8501",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(tickets_router.router)

    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "healthy", "service": "TriageFlow API"}

    return app


app = create_app()
