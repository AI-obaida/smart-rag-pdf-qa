import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected",
    [
        (
            "Students must use Flask only if approved.",
            "Students must use Flask.",
            False,
        ),
        (
            "Students must use Flask unless exempted.",
            "Students must use Flask without exceptions.",
            False,
        ),
        (
            "Students must install Flask.",
            "Students must use Flask.",
            False,
        ),
        (
            "Students must not use Flask. Students must use Django.",
            "Students must use Django.",
            True,
        ),
        (
            "Students must use Flask only if approved.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            False,
        ),
        (
            "Students must use Flask unless exempted.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            False,
        ),
    ],
)
def test_modality_conditions(source, claim, expected):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["allowed"] is expected
