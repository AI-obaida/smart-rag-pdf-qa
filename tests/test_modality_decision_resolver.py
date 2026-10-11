import pytest

from app.services.modality_decision_resolver import ModalityDecisionResolver


@pytest.mark.parametrize(
    "modality_verdict, modality_reason, conflict_verdict, expected",
    [
        ("REJECT", "no_matching_source_statement", "UNKNOWN", "NOT_APPLICABLE"),
        ("REJECT", "no_matching_source_statement", "CONFLICT", "REJECT"),
        ("REJECT", "mandatory_overstatement", "UNKNOWN", "REJECT"),
        ("REJECT", "negation_conflict", "UNKNOWN", "REJECT"),
        ("PASS", "matching_mandatory_statement", "UNKNOWN", "PASS"),
        ("PASS", "matching_mandatory_statement", "CONFLICT", "REJECT"),
        ("NOT_APPLICABLE", "no_mandatory_overstatement_detected", "UNKNOWN", "NOT_APPLICABLE"),
        ("NOT_APPLICABLE", "no_mandatory_overstatement_detected", "CONFLICT", "REJECT"),
        ("REJECT", "no_matching_source_statement", "NO_CONFLICT", "NOT_APPLICABLE"),
        ("PASS", "matching_mandatory_statement", "NO_CONFLICT", "PASS"),
    ],
)
def test_modality_decision_resolution(
    modality_verdict,
    modality_reason,
    conflict_verdict,
    expected,
):
    result = ModalityDecisionResolver().resolve(
        modality_result={
            "verdict": modality_verdict,
            "reason": modality_reason,
        },
        conflict_result={
            "verdict": conflict_verdict,
        },
    )

    assert result["verdict"] == expected


@pytest.mark.parametrize(
    "modality_result, conflict_result",
    [
        ({}, {"verdict": "UNKNOWN"}),
        ({"verdict": "PASS", "reason": "ok"}, {}),
        (None, {"verdict": "UNKNOWN"}),
        ({"verdict": "PASS", "reason": "ok"}, None),
    ],
)
def test_invalid_resolution_inputs(
    modality_result,
    conflict_result,
):
    with pytest.raises((TypeError, ValueError)):
        ModalityDecisionResolver().resolve(
            modality_result=modality_result,
            conflict_result=conflict_result,
        )
