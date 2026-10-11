import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source, claim, expected",
    [
        (
            "Students must use Flask if they choose the Flask track.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 "
            "\u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask "
            "\u0625\u0630\u0627 \u0627\u062e\u062a\u0627\u0631\u0648\u0627 "
            "\u0645\u0633\u0627\u0631 Flask.",
            "NOT_APPLICABLE",
        ),
        (
            "Students must use Flask if they choose the Flask track.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 "
            "\u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            "NOT_APPLICABLE",
        ),
        (
            "Students must use Flask.",
            "The project must use Django.",
            "NOT_APPLICABLE",
        ),
        (
            "Students should discuss the project idea.",
            "Students must discuss the project idea.",
            "REJECT",
        ),
        (
            "Students must use Flask.",
            "Students must use Flask.",
            "PASS",
        ),
    ],
)
def test_uncertainty_policy(source, claim, expected):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["verdict"] == expected
