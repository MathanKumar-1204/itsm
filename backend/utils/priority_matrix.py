"""
ITIL-compliant deterministic Priority Matrix.
Calculates final ticket priority based on verified Impact and Urgency levels.
"""

from typing import Literal

VALID_LEVELS = {"critical", "high", "medium", "low"}

# ITIL Standard 4x4 Priority Matrix:
# [Impact][Urgency] -> Priority
PRIORITY_MATRIX = {
    "critical": {
        "critical": "critical",
        "high": "critical",
        "medium": "high",
        "low": "medium",
    },
    "high": {
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "low": "low",
    },
    "medium": {
        "critical": "high",
        "high": "medium",
        "medium": "medium",
        "low": "low",
    },
    "low": {
        "critical": "medium",
        "high": "low",
        "medium": "low",
        "low": "low",
    },
}


def calculate_priority(impact: str, urgency: str) -> str:
    """
    Calculates deterministic priority according to standard ITIL 4-tier matrix.
    Defaults to 'medium' if inputs are invalid.
    """
    impact_clean = (impact or "").strip().lower()
    urgency_clean = (urgency or "").strip().lower()

    if impact_clean not in VALID_LEVELS:
        impact_clean = "medium"
    if urgency_clean not in VALID_LEVELS:
        urgency_clean = "medium"

    return PRIORITY_MATRIX[impact_clean][urgency_clean]
