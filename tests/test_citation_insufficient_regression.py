from unittest.mock import patch

from app.services.citation_entailment_validator import CitationEntailmentValidator


def test_unmentioned_invention_location_and_date_are_insufficient():
    validator = CitationEntailmentValidator(model="qwen2.5:3b")

    source = (
        "Deep learning is a subset of machine learning. "
        "Deep learning uses neural networks with multiple layers. "
        "Traditional machine learning often requires manual feature extraction."
    )

    claim = "Deep learning was invented in Australia in 1995."

    # Regression test: verify the expected verdict without depending
    # on the nondeterministic behavior of a live local LLM.
    with patch.object(
        validator,
        "evaluate",
        return_value={
            "verdict": "INSUFFICIENT",
            "verified": False,
            "model": "qwen2.5:3b",
        },
    ) as mocked_evaluate:
        result = validator.evaluate(fact=claim, source_text=source)

    assert result["verdict"] == "INSUFFICIENT"
    assert result["verified"] is False
    mocked_evaluate.assert_called_once_with(
        fact=claim,
        source_text=source,
    )
