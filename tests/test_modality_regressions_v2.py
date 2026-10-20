import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source, claim, expected",
    [
        (
            "Students must not use Flask. They may use Django if approved.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            "REJECT",
        ),
        (
            "Students must not use Django.",
            "The project must use Django.",
            "REJECT",
        ),
        (
            "Students must use Django.",
            "The project must use Django.",
            "NOT_APPLICABLE",
        ),
        (
            "Students must use Flask. Students must use Django.",
            "The project must use Django.",
            "NOT_APPLICABLE",
        ),
        (
            "Students must use Flask.",
            "The project must use Django.",
            "NOT_APPLICABLE",
        ),
        (
            "Students must not use Flask. Students must use Django.",
            "Students must use Django.",
            "PASS",
        ),
    ],
)
def test_modality_regressions_v2(source, claim, expected):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )
    assert result["verdict"] == expected
