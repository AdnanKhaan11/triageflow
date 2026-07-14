"""
backend/agents/retrieval_agent.py

Retrieves relevant manual/SOP chunks from the vector store for a
given maintenance ticket.
"""

from __future__ import annotations

from backend.services.vector_store import VectorStoreClient

# Created ONCE at module load time -- not inside retrieve_node -- so
# we don't reload the embedding model and reconnect to Chroma on
# every single call. Same principle as llm_client.py's module-level
# `llm` object.
vector_store_client = VectorStoreClient()


def retrieve_node(state: dict) -> dict:
    """
    Reads state['raw_text'] (and optionally state['classification']),
    queries the vector store, and returns a partial state update with
    'retrieved_chunks' populated.
    """
    raw_text = state.get("raw_text", "")
    classification = state.get("classification", {})

    # For now, query using the raw ticket text directly. A
    # reformulated query (e.g. f"{equipment_id} {fault_type}
    # troubleshooting") is worth A/B testing later -- see TODO #2 in
    # the original scaffold notes.
    query_text = raw_text

    retrieved_chunks = vector_store_client.query(query_text, top_k=5)

    # Debug visibility during development -- keep this print while
    # you're still validating retrieval quality by hand.
    print(f"Retrieved {len(retrieved_chunks)} chunks for query: '{query_text}'")
    for chunk in retrieved_chunks:
        print(
            f"  source={chunk['source']} page={chunk.get('page')} -> {chunk['text'][:80]}..."
        )

    return {"retrieved_chunks": retrieved_chunks}


if __name__ == "__main__":
    test_state = {
        "raw_text": "Pump P-204 making loud noise, vibration increasing since yesterday.",
        "classification": {
            "equipment_id": "P-204",
            "fault_type": "vibration",
            "urgency": "medium",
            "confidence": 0.85,
        },
    }
    result = retrieve_node(test_state)
    print()
    print("Final returned dict:", result)
