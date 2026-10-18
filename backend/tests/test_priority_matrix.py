import pytest
from utils.priority_matrix import calculate_priority, PRIORITY_MATRIX


def test_priority_matrix_critical_combinations():
    assert calculate_priority("critical", "critical") == "critical"
    assert calculate_priority("critical", "high") == "critical"
    assert calculate_priority("high", "critical") == "critical"
    assert calculate_priority("critical", "medium") == "high"
    assert calculate_priority("critical", "low") == "medium"


def test_priority_matrix_standard_cells():
    assert calculate_priority("high", "high") == "high"
    assert calculate_priority("high", "medium") == "medium"
    assert calculate_priority("medium", "high") == "medium"
    assert calculate_priority("medium", "medium") == "medium"
    assert calculate_priority("low", "low") == "low"
    assert calculate_priority("low", "medium") == "low"
    assert calculate_priority("low", "critical") == "medium"


def test_priority_matrix_case_insensitivity_and_whitespace():
    assert calculate_priority("CRITICAL ", " high") == "critical"
    assert calculate_priority("  Medium  ", "LOW") == "low"


def test_priority_matrix_fallback_on_invalid_inputs():
    # If invalid level is supplied, defaults safely to medium
    assert calculate_priority("invalid_level", "critical") == "high" # medium + critical = high
    assert calculate_priority("unknown", "unknown") == "medium"
    assert calculate_priority("", None) == "medium"
