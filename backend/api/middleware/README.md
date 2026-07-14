# backend/api/middleware/

## Purpose (placeholder folder)
Custom FastAPI middleware — things that wrap EVERY request, like
request logging, timing, or error formatting.

## Suggested first middleware (good learning exercise)
A simple request-timing + structured-logging middleware that logs:
method, path, status code, and duration for every request. This pairs
directly with triageFlow_plan.md section 20 ("Monitoring &
Observability") — it's a small piece of real observability you can
point to.

## TODO
1. Write a middleware function/class that wraps each request,
   measures duration, and logs it.
2. Register it in backend/api/main.py via `app.add_middleware(...)` or
   `@app.middleware("http")`.

## Learning objective
Understand the difference between route-level logic and
cross-cutting middleware logic — and recognize which of your future
features belong in which place.
