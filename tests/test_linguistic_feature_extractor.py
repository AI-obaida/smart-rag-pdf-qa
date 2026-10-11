import pytest

from app.services.linguistic_feature_extractor import (
    LinguisticFeatureExtractor,
)


@pytest.mark.parametrize(
    "statement,expected",
    [
        (
            "Students must use Flask.",
            ("MUST", False, False, False),
        ),
        (
            "Students must not use Flask.",
            ("MUST", True, False, False),
        ),
        (
            "Students should use Flask.",
            ("SHOULD", False, False, False),
        ),
        (
            "Students must use Flask if approved.",
            ("MUST", False, True, False),
        ),
        (
            "Students must use Flask unless exempted.",
            ("MUST", False, False, True),
        ),
        (
            "\u064a\u062c\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            ("MUST", False, False, False),
        ),
        (
            "\u064a\u062c\u0628 \u0623\u0644\u0627 \u064a\u0633\u062a\u062e\u062f\u0645 \u0627\u0644\u0637\u0644\u0627\u0628 Flask.",
            ("MUST", True, False, False),
        ),
        (
            "\u064a\u064f\u0646\u0635\u062d \u0627\u0644\u0637\u0644\u0627\u0628 \u0628\u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask.",
            ("SHOULD", False, False, False),
        ),
        (
            "\u064a\u062c\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask \u0625\u0630\u0627 \u062a\u0645 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631.",
            ("MUST", False, True, False),
        ),
        (
            "\u064a\u062c\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Flask \u0645\u0627 \u0644\u0645 \u064a\u062a\u0645 \u0627\u0644\u0625\u0639\u0641\u0627\u0621.",
            ("MUST", False, False, True),
        ),
        (
            "The word mustard appears here.",
            ("NONE", False, False, False),
        ),
        (
            "Use Flask unless exempted.",
            ("NONE", False, False, True),
        ),
        (
            "Use Flask if approved.",
            ("NONE", False, True, False),
        ),
        (
            "The framework is Flask.",
            ("NONE", False, False, False),
        ),
    ],
)
def test_extract_linguistic_features(statement, expected):
    result = LinguisticFeatureExtractor().extract(statement)

    actual = (
        result["modality"],
        result["negated"],
        result["conditional"],
        result["exception"],
    )

    assert actual == expected


@pytest.mark.parametrize("invalid", ["", "   ", None, 123])
def test_reject_invalid_input(invalid):
    with pytest.raises((TypeError, ValueError)):
        LinguisticFeatureExtractor().extract(invalid)
