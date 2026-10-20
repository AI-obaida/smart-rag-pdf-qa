import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected_reason",
    [
        (
            "Students must not use Django.",
            "Students must use Django.",
            "explicit_prohibition_conflict",
        ),
        (
            "Students must not use Flask or Django.",
            "Students must use Django.",
            "explicit_prohibition_conflict",
        ),
        (
            "Students must not use Flask with Django.",
            "Students must use Django.",
            "no_matching_source_statement",
        ),
        (
            "Students must not use Flask with Django.",
            "Students must use Flask with Django.",
            "explicit_prohibition_conflict",
        ),
    ],
)
def test_prohibition_reason(source, claim, expected_reason):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["verdict"] == "REJECT"
    assert result["reason"] == expected_reason
