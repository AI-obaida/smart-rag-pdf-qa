import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected",
    [
        (
            "Students must use Flask.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            True,
        ),
        (
            "Students should use Flask.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            False,
        ),
        (
            "Students must not use Flask.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            False,
        ),
        (
            "Students must use Django.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            False,
        ),
        (
            "Students must submit a report. "
            "Students should use Flask.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            False,
        ),
    ],
)
def test_cross_language_modality(source, claim, expected):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["allowed"] is expected
