import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected_reason",
    [
        (
            "Teachers must not use Django.",
            "Students must use Django.",
            "no_matching_source_statement",
        ),
        (
            "Students must not use Django.",
            "Teachers must use Django.",
            "no_matching_source_statement",
        ),
        (
            "Students must not use Django.",
            "Students must use Django.",
            "explicit_prohibition_conflict",
        ),
    ],
)
def test_prohibition_subject_scope(source, claim, expected_reason):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["verdict"] == "REJECT"
    assert result["reason"] == expected_reason

@pytest.mark.parametrize(
    "source,claim,expected_reason",
    [
        (
            "Teachers must not use Django.",
            "Students must use Django.",
            "no_matching_source_statement",
        ),
        (
            "Students must not use Django.",
            "Teachers must use Django.",
            "no_matching_source_statement",
        ),
    ],
)
def test_prohibition_subject_scope_additional(
    source, claim, expected_reason
):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["verdict"] == "REJECT"
    assert result["reason"] == expected_reason
