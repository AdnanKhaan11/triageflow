"""
backend/agents/inventory_agent.py

Mocked spare-parts inventory lookup, keyed by equipment_id.
"""

from __future__ import annotations

from backend.graphs.state import TicketState

# eta_days = mock estimate of how long it would take to get parts if
# they are NOT currently available. None means "unknown equipment,
# no data."
MOCK_INVENTORY = {
    "P-204": {"parts_available": True, "eta_days": 2},
    "P-207": {"parts_available": False, "eta_days": 5},
    "P-318": {"parts_available": True, "eta_days": 1},
    "C-11": {"parts_available": False, "eta_days": 7},
    "C-22": {"parts_available": True, "eta_days": 3},
    "C-305": {"parts_available": False, "eta_days": 10},
    "M-18": {"parts_available": True, "eta_days": 1},
    "M-44": {"parts_available": True, "eta_days": 2},
    "M-091": {"parts_available": False, "eta_days": 14},
    "T-501": {"parts_available": False, "eta_days": 21},
    "V-118": {"parts_available": True, "eta_days": 1},
    "HX-77": {"parts_available": True, "eta_days": 4},
    "MCC-14": {"parts_available": False, "eta_days": 6},
}


def get_inventory_status(equipment_id: str) -> dict:
    """
    Mock function to check inventory status for a given equipment ID.
    Returns a dict with 'parts_available' and 'eta_days'.
    """
    return MOCK_INVENTORY.get(
        equipment_id,
        {"parts_available": False, "eta_days": None},
    )


def check_inventory_node(state: TicketState) -> dict:
    """
    Reads state['classification']['equipment_id'], looks up mock
    inventory data, and returns a partial state update with
    'inventory_check' populated.
    """
    classification = state.get("classification", {})
    equipment_id = classification.get("equipment_id")

    inventory_status = get_inventory_status(equipment_id)

    return {"inventory_check": inventory_status}


if __name__ == "__main__":
    test_state = {
        "classification": {
            "equipment_id": "P-204",
            "fault_type": "vibration",
            "urgency": "medium",
            "confidence": 0.85,
        }
    }
    print(check_inventory_node(test_state))

    # Test the "unknown equipment" fallback path too
    unknown_state = {"classification": {"equipment_id": "X-999"}}
    print(check_inventory_node(unknown_state))
