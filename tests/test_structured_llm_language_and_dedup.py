import json
from unittest.mock import patch

from app.services.structured_llm_service import StructuredLLMService


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def generate_with_mock(question, facts):
    captured = {}

    def fake_urlopen(request, timeout):
        payload = json.loads(request.data.decode("utf-8"))
        captured["payload"] = payload

        return FakeResponse({
            "done_reason": "stop",
            "message": {
                "content": json.dumps({
                    "items": [
                        {"fact": fact, "source_id": "S1"}
                        for fact in facts
                    ]
                })
            },
        })

    service = StructuredLLMService()

    chunks = [{
        "page_number": 1,
        "chunk_text": "Django and Flask are backend frameworks.",
    }]

    with patch(
        "app.services.structured_llm_service.urllib.request.urlopen",
        side_effect=fake_urlopen,
    ):
        result = service.generate(question, chunks)

    return captured["payload"], result


def test_english_question_explicitly_sets_english():
    payload, _ = generate_with_mock(
        "Which backend frameworks are mentioned?",
        ["Django and Flask are mentioned."],
    )

    final_message = payload["messages"][-1]["content"]
    assert "English" in final_message


def test_arabic_question_explicitly_sets_arabic():
    payload, _ = generate_with_mock(
        "\u0645\u0627 \u0623\u0637\u0631 \u0627\u0644\u062e\u0644\u0641\u064a\u0629\u061f",
        ["Django and Flask"],
    )

    final_message = payload["messages"][-1]["content"]
    assert "Arabic" in final_message


def test_removes_exact_duplicate_facts():
    _, result = generate_with_mock(
        "Which backend frameworks?",
        [
            "Django and Flask are backend frameworks.",
            "Django and Flask are backend frameworks.",
        ],
    )

    assert len(result["items"]) == 1


def test_removes_case_and_whitespace_duplicates():
    _, result = generate_with_mock(
        "Which backend frameworks?",
        [
            "Django and Flask are backend frameworks.",
            "  django   and flask are backend frameworks.  ",
        ],
    )

    assert len(result["items"]) == 1


def test_preserves_distinct_facts():
    _, result = generate_with_mock(
        "Which backend frameworks?",
        [
            "Django is a backend framework.",
            "Flask is a backend framework.",
        ],
    )

    assert len(result["items"]) == 2
