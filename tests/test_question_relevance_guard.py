import io
import json
from unittest.mock import patch

import pytest

from app.services.question_relevance_guard import QuestionRelevanceGuard


def fake_response(verdict, done_reason="stop"):
    return io.BytesIO(
        json.dumps({
            "done_reason": done_reason,
            "message": {
                "content": json.dumps({"verdict": verdict})
            },
        }).encode("utf-8")
    )


@pytest.mark.parametrize(
    "verdict,expected",
    [
        ("RELEVANT", True),
        ("IRRELEVANT", False),
    ],
)
def test_valid_relevance_verdicts(verdict, expected):
    guard = QuestionRelevanceGuard()

    with patch(
        "app.services.question_relevance_guard."
        "urllib.request.urlopen",
        return_value=fake_response(verdict),
    ):
        result = guard.evaluate(
            question="Which backend frameworks are mentioned?",
            fact="Django and Flask are backend frameworks.",
        )

    assert result["verdict"] == verdict
    assert result["relevant"] is expected


def test_rejects_empty_question():
    guard = QuestionRelevanceGuard()

    with pytest.raises(ValueError):
        guard.evaluate("", "Django is a framework.")


def test_rejects_empty_fact():
    guard = QuestionRelevanceGuard()

    with pytest.raises(ValueError):
        guard.evaluate("Which frameworks?", "")


def test_rejects_unknown_verdict():
    guard = QuestionRelevanceGuard()

    with patch(
        "app.services.question_relevance_guard."
        "urllib.request.urlopen",
        return_value=fake_response("UNKNOWN"),
    ):
        with pytest.raises(ValueError):
            guard.evaluate("Which frameworks?", "Django.")


def test_rejects_incomplete_model_response():
    guard = QuestionRelevanceGuard()

    with patch(
        "app.services.question_relevance_guard."
        "urllib.request.urlopen",
        return_value=fake_response(
            "RELEVANT",
            done_reason="length",
        ),
    ):
        with pytest.raises(RuntimeError):
            guard.evaluate("Which frameworks?", "Django.")


def test_connection_failure_is_not_silently_accepted():
    guard = QuestionRelevanceGuard()

    with patch(
        "app.services.question_relevance_guard."
        "urllib.request.urlopen",
        side_effect=ConnectionError("Ollama unavailable"),
    ):
        with pytest.raises(ConnectionError):
            guard.evaluate("Which frameworks?", "Django.")


def test_payload_contains_question_and_fact():
    guard = QuestionRelevanceGuard()
    captured = {}

    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(
            request.data.decode("utf-8")
        )
        return fake_response("RELEVANT")

    with patch(
        "app.services.question_relevance_guard."
        "urllib.request.urlopen",
        side_effect=fake_urlopen,
    ):
        guard.evaluate(
            question="Which backend frameworks are mentioned?",
            fact="Django and Flask are backend frameworks.",
        )

    payload = captured["payload"]

    assert payload["model"] == "qwen2.5:3b"
    assert payload["stream"] is False

    prompt = payload["messages"][0]["content"]

    assert "Which backend frameworks are mentioned?" in prompt
    assert "Django and Flask are backend frameworks." in prompt
