from app.services.citation_entailment_validator import CitationEntailmentValidator


def test_live_validator_handles_supported_contradicted_and_missing_evidence():
    validator = CitationEntailmentValidator(model="qwen2.5:3b")

    source = (
        "Deep learning is a subset of machine learning. "
        "Deep learning uses neural networks with multiple layers."
    )

    cases = [
        (
            "SUPPORTED",
            "Deep learning uses neural networks with multiple layers.",
        ),
        (
            "CONTRADICTED",
            "Deep learning is not a subset of machine learning.",
        ),
        (
            "INSUFFICIENT",
            "Deep learning was invented in Australia in 1995.",
        ),
    ]

    for expected, claim in cases:
        result = validator.evaluate(fact=claim, source_text=source)
        assert result["verdict"] == expected, (
            f"Claim: {claim!r}; expected {expected}, "
            f"received {result['verdict']}"
        )
