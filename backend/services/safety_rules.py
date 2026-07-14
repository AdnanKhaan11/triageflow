from __future__ import annotations

from typing import Dict, Any

"""
backend/services/safety_rules.py

RESPONSIBILITY
---------------
Hard-coded, deterministic safety override rules that run AFTER the
LLM classification step and can force a ticket's urgency to
"critical" regardless of what the LLM decided."""


CRITICAL_TRIGGER_PHRASES: list[str] = [
    "gas leak",
    "fire",
    "explosion",
    "smoke",
    "toxic fumes",
    "chemical spill",
    "electrical hazard",
    "structural damage",
]


class SafetyOverride:
    def __init__(self, trigger_phrases: list[str] = CRITICAL_TRIGGER_PHRASES):
        self.trigger_phrases = trigger_phrases

    def apply_safety_override(
        self, raw_text: str, classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        modified_classification = classification.copy()
        modified_classification["safety_override_applied"] = False
        text_lower = raw_text.lower()

        matched_phrases = []
        for phrase in self.trigger_phrases:
            if phrase in text_lower:
                matched_phrases.append(phrase)

        if matched_phrases:
            modified_classification["urgency"] = "critical"
            modified_classification["safety_override_applied"] = True
            modified_classification["safety_override_triggers"] = matched_phrases
            modified_classification["safety_override_reason"] = (
                "Critical safety phrase(s) detected"
            )

        return modified_classification
