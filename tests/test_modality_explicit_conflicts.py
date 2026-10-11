import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected",
    [
        (
            "Students must not use Flask.",
            "Students must use Flask.",
            "REJECT",
        ),
        (
            "Students must use Flask.",
            "Students must not use Flask.",
            "REJECT",
        ),
        (
            "Students must use Flask only if approved.",
            "Students must use Flask.",
            "REJECT",
        ),
        (
            "Students must use Flask unless exempted.",
            "Students must use Flask without exceptions.",
            "REJECT",
        ),
        (
            "Students should use Flask.",
            "Students must use Flask.",
            "REJECT",
        ),
        (
            "Students must use Flask.",
            "Students must use Flask.",
            "PASS",
        ),
    ],
)
def test_explicit_modality_conflicts(source, claim, expected):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["verdict"] == expected
