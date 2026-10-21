
import json
from unittest.mock import patch

from app.services.citation_entailment_validator import CitationEntailmentValidator


def test_missing_information_is_not_explicit_contradiction():
    captured = {}

    def fake_urlopen(request, **kwargs):
        payload = json.loads(request.data.decode("utf-8"))
        captured["prompt"] = payload["messages"][0]["content"]
        raise RuntimeError("PROMPT_CAPTURED")

    validator = CitationEntailmentValidator()

    with patch(
        "urllib.request.urlopen",
        side_effect=fake_urlopen,
    ):
        try:
            validator.evaluate(
                fact="Deep learning was invented in Australia in 1995.",
                source_text="Deep learning uses multilayer neural networks.",
            )
        except RuntimeError as exc:
            assert str(exc) == "PROMPT_CAPTURED"

    prompt = captured["prompt"]

    assert "Absence of evidence is not evidence of contradiction." in prompt
    assert "If SOURCE does not mention" in prompt
