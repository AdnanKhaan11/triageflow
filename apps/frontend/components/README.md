# apps/frontend/components/

## Purpose (placeholder folder)
Reusable Streamlit UI pieces shared across pages — e.g. a
"ticket card" component, an "urgency badge" component (color-coded by
urgency level), or a "source citation" component.

## Suggested first component (good learning exercise)
An `urgency_badge(urgency: str) -> None` function that renders a
colored badge (e.g. red for critical, orange for high, green for low)
— small, reusable, and used on both submit_ticket.py confirmation and
review_queue.py's ticket list.

## TODO
Extract components here once you notice yourself copy-pasting the
same Streamlit rendering code across submit_ticket.py and
review_queue.py — don't build this speculatively before that happens.
