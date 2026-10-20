import pytest

from app.services.structured_rag_service import StructuredRAGService


validate = StructuredRAGService._translation_preserves_known_terms


@pytest.mark.parametrize(
    "question,translation,expected",
    [
        (
            "\u0645\u0627 \u0627\u0644\u0641\u0631\u0642 "
            "\u0628\u064a\u0646 \u0627\u0644\u062a\u0639\u0644\u0645 "
            "\u0627\u0644\u0622\u0644\u064a \u0648\u0627\u0644\u062a\u0639\u0644\u0645 "
            "\u0627\u0644\u0639\u0645\u064a\u0642\u061f",
            "What is the difference between machine learning and deep learning?",
            True,
        ),
        (
            "\u0645\u0627 \u0627\u0644\u0641\u0631\u0642 "
            "\u0628\u064a\u0646 \u0627\u0644\u062a\u0639\u0644\u0645 "
            "\u0627\u0644\u0622\u0644\u064a \u0648\u0627\u0644\u062a\u0639\u0644\u0645 "
            "\u0627\u0644\u0639\u0645\u064a\u0642\u061f",
            "What is the difference between a car and a truck?",
            False,
        ),
        (
            "\u0641\u064a \u0627\u0644\u062a\u0639\u0644\u0645 "
            "\u0627\u0644\u0622\u0644\u064a \u0627\u0644\u062a\u0642\u0644\u064a\u062f\u064a\u060c "
            "\u0645\u0627\u0630\u0627 \u064a\u062d\u062f\u062b "
            "\u0628\u0639\u062f \u0627\u0633\u062a\u062e\u0631\u0627\u062c "
            "\u0627\u0644\u062e\u0635\u0627\u0626\u0635\u061f",
            "In traditional machine learning, what happens after feature extraction?",
            True,
        ),
        (
            "\u0645\u0627 \u0645\u0639\u0646\u0649 "
            "\u0627\u0644\u062d\u064a\u0627\u0629\u061f",
            "What is the meaning of life?",
            True,
        ),
        (
            "\u0645\u0627 \u0645\u0639\u0646\u0649 "
            "\u0627\u0644\u062d\u064a\u0627\u0629\u061f",
            "",
            False,
        ),
    ],
)
def test_translation_known_term_validation(question, translation, expected):
    assert validate(question, translation) is expected


def test_invalid_input_is_rejected():
    assert validate(None, "machine learning") is False
    assert validate("question", None) is False
