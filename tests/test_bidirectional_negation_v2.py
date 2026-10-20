import pytest

from app.services.modality_decision_resolver import ModalityDecisionResolver


@pytest.mark.parametrize(
    "source_negated,fact_negated,expected",
    [
        (False, True, "REJECT"),
        (True, False, "REJECT"),
        (False, False, "PASS"),
        (True, True, "PASS"),
    ],
)
def test_bidirectional_negation(
    source_negated, fact_negated, expected
):
    resolver = ModalityDecisionResolver()

    result = resolver.resolve(
        {"verdict": "PASS", "reason": "matching_statement"},
        {"verdict": "NO_CONFLICT", "reason": "no_conflict"},
        source_features={"negated": source_negated},
        fact_features={"negated": fact_negated},
    )

    assert result["verdict"] == expected
