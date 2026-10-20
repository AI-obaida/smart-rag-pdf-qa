from app.services.search_query_translator import SearchQueryTranslator


def test_arabic_ml_translation_preserves_topic():
    question = (
        "\u0645\u0627 \u0627\u0644\u0641\u0631\u0642 "
        "\u0628\u064a\u0646 \u0627\u0644\u062a\u0639\u0644\u0645 "
        "\u0627\u0644\u0622\u0644\u064a \u0648\u0627\u0644\u062a\u0639\u0644\u0645 "
        "\u0627\u0644\u0639\u0645\u064a\u0642\u061f"
    )

    result = SearchQueryTranslator().translate(question).lower()

    assert "machine learning" in result
    assert "deep learning" in result


def test_arabic_feature_extraction_translation_preserves_topic():
    question = (
        "\u0641\u064a \u0627\u0644\u062a\u0639\u0644\u0645 "
        "\u0627\u0644\u0622\u0644\u064a \u0627\u0644\u062a\u0642\u0644\u064a\u062f\u064a\u060c "
        "\u0645\u0627\u0630\u0627 \u064a\u062d\u062f\u062b "
        "\u0628\u0639\u062f \u0627\u0633\u062a\u062e\u0631\u0627\u062c "
        "\u0627\u0644\u062e\u0635\u0627\u0626\u0635\u061f"
    )

    result = SearchQueryTranslator().translate(question).lower()

    assert "feature" in result
    assert "machine learning" in result or "learning" in result
    assert "car and a truck" not in result
    assert "civil engineer" not in result
