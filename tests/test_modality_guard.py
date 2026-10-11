import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected",
    [
        (
            "Students must use Flask.",
            "Students must use Flask.",
            True,
        ),
        (
            "Students should discuss the project idea.",
            "Students must discuss the project idea.",
            False,
        ),
        (
            "Students may use Flask.",
            "Students must use Flask.",
            False,
        ),
        (
            "Students should discuss the project idea.",
            "Students should discuss the project idea.",
            True,
        ),
        (
            "Students should discuss the project idea.",
            "Students are required to discuss the project idea.",
            False,
        ),
        (
            "Students should discuss the project idea.",
            "Students have to discuss the project idea.",
            False,
        ),
        (
            "Students should discuss the project idea.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0645\u0646\u0627\u0642\u0634\u0629 \u0641\u0643\u0631\u0629 \u0627\u0644\u0645\u0634\u0631\u0648\u0639.",
            False,
        ),
        (
            "Students must use Flask.",
            "\u064a\u062c\u0628 \u0639\u0644\u0649 \u0627\u0644\u0637\u0644\u0627\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            True,
        ),
    ],
)
def test_modality_guard(source, claim, expected):
    guard = ModalityGuard()

    result = guard.evaluate(
        fact=claim,
        source_text=source,
    )

    assert result["allowed"] is expected


def test_rejects_empty_source():
    guard = ModalityGuard()

    with pytest.raises(ValueError):
        guard.evaluate(
            fact="Students must use Flask.",
            source_text="",
        )


def test_rejects_empty_claim():
    guard = ModalityGuard()

    with pytest.raises(ValueError):
        guard.evaluate(
            fact="",
            source_text="Students must use Flask.",
        )
