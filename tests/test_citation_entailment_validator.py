import io
import json
from unittest.mock import patch

import pytest

from app.services.citation_entailment_validator import (
    CitationEntailmentValidator,
)


def mock_response(content, done_reason="stop"):
    payload = {
        "done_reason": done_reason,
        "message": {"content": content},
    }
    return io.BytesIO(json.dumps(payload).encode("utf-8"))


@pytest.mark.parametrize(
    "verdict,verified",
    [
        ("SUPPORTED", True),
        ("CONTRADICTED", False),
        ("INSUFFICIENT", False),
    ],
)
def test_valid_verdicts(verdict, verified):
    validator = CitationEntailmentValidator()

    response = mock_response(
        json.dumps({"verdict": verdict})
    )

    with patch(
        "app.services.citation_entailment_validator."
        "urllib.request.urlopen",
        return_value=response,
    ):
        result = validator.evaluate(
            "The project requires a backend.",
            "The project must include a backend framework.",
        )

    assert result["verdict"] == verdict
    assert result["verified"] is verified
    assert result["model"] == "qwen2.5:3b"


def test_empty_fact():
    validator = CitationEntailmentValidator()

    with pytest.raises(ValueError):
        validator.evaluate("", "Valid source")


def test_empty_source():
    validator = CitationEntailmentValidator()

    with pytest.raises(ValueError):
        validator.evaluate("Valid fact", "")


def test_invalid_json():
    validator = CitationEntailmentValidator()

    with patch(
        "app.services.citation_entailment_validator."
        "urllib.request.urlopen",
        return_value=mock_response("not-json"),
    ):
        with pytest.raises(json.JSONDecodeError):
            validator.evaluate("Fact", "Source")


def test_invalid_verdict():
    validator = CitationEntailmentValidator()

    response = mock_response(
        json.dumps({"verdict": "UNKNOWN"})
    )

    with patch(
        "app.services.citation_entailment_validator."
        "urllib.request.urlopen",
        return_value=response,
    ):
        with pytest.raises(ValueError):
            validator.evaluate("Fact", "Source")


def test_incomplete_response():
    validator = CitationEntailmentValidator()

    response = mock_response(
        json.dumps({"verdict": "SUPPORTED"}),
        done_reason="length",
    )

    with patch(
        "app.services.citation_entailment_validator."
        "urllib.request.urlopen",
        return_value=response,
    ):
        with pytest.raises(RuntimeError):
            validator.evaluate("Fact", "Source")


def test_connection_failure():
    validator = CitationEntailmentValidator()

    with patch(
        "app.services.citation_entailment_validator."
        "urllib.request.urlopen",
        side_effect=ConnectionError("Ollama unavailable"),
    ):
        with pytest.raises(ConnectionError):
            validator.evaluate("Fact", "Source")
