import pytest

from app.services.modality_decision_resolver import ModalityDecisionResolver


@pytest.mark.parametrize(
    "source_features, fact_features, expected",
    [
        (
            {
                "modality": "MUST",
                "negated": False,
                "conditional": False,
                "exception": False,
            },
            {
                "modality": "MUST",
                "negated": True,
                "conditional": False,
                "exception": False,
            },
            "REJECT",
        ),
        (
            {
                "modality": "SHOULD",
                "negated": False,
                "conditional": False,
                "exception": False,
            },
            {
                "modality": "MUST",
                "negated": False,
                "conditional": False,
                "exception": False,
            },
            "REJECT",
        ),
        (
            {
                "modality": "MUST",
                "negated": False,
                "conditional": True,
                "exception": False,
            },
            {
                "modality": "MUST",
                "negated": False,
                "conditional": False,
                "exception": False,
            },
            "REJECT",
        ),
        (
            {
                "modality": "MUST",
                "negated": False,
                "conditional": False,
                "exception": False,
            },
            {
                "modality": "MUST",
                "negated": False,
                "conditional": False,
                "exception": False,
            },
            "PASS",
        ),
    ],
)
def test_feature_safety(source_features, fact_features, expected):
    result = ModalityDecisionResolver().resolve(
        modality_result={
            "verdict": "PASS",
            "reason": "matching_mandatory_statement",
        },
        conflict_result={
            "verdict": "UNKNOWN",
        },
        source_features=source_features,
        fact_features=fact_features,
    )

    assert result["verdict"] == expected
