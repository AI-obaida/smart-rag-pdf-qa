import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected",
    [
        (
            "The project must use Django or Flask. "
            "Students should discuss the project idea.",
            "Students must discuss the project idea.",
            False,
        ),
        (
            "The project must use Django or Flask. "
            "Students should discuss the project idea.",
            "The project must use Django or Flask.",
            True,
        ),
        (
            "Students must not use Flask.",
            "Students must use Flask.",
            False,
        ),
        (
            "Students must submit a report. "
            "Students may use Flask.",
            "Students must use Flask.",
            False,
        ),
    ],
)
def test_modality_edge_cases(source, claim, expected):
    guard = ModalityGuard()

    result = guard.evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["allowed"] is expected
