import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected_verdict",
    [
        (
            "Students must use Flask.",
            "Students must use Flask.",
            "PASS",
        ),
        (
            "Students should use Flask.",
            "Students must use Flask.",
            "REJECT",
        ),
        (
            "Students must not use Flask.",
            "Students must use Flask.",
            "REJECT",
        ),
        (
            "Students should discuss the project idea.",
            "Students should discuss the project idea.",
            "NOT_APPLICABLE",
        ),
        (
            "Students must use Flask.",
            "The project uses PostgreSQL.",
            "NOT_APPLICABLE",
        ),
        (
            "Students must use Flask.",
            "Students should submit a mobile application.",
            "NOT_APPLICABLE",
        ),
    ],
)
def test_modality_verdicts(source, claim, expected_verdict):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["verdict"] == expected_verdict
    assert result["allowed"] is (expected_verdict != "REJECT")
