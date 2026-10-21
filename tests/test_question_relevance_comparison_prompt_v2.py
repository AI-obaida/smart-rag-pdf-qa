import json
from unittest.mock import patch

from app.services.question_relevance_guard import QuestionRelevanceGuard


def test_comparison_prompt_requires_subject_relevance():
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout):
        captured.update(
            json.loads(request.data.decode("utf-8"))
        )
        return FakeResponse()

    def fake_json_load(response):
        return {
            "done_reason": "stop",
            "message": {
                "content": json.dumps({"verdict": "RELEVANT"})
            },
        }

    with patch(
        "app.services.question_relevance_guard.urllib.request.urlopen",
        side_effect=fake_urlopen,
    ), patch(
        "app.services.question_relevance_guard.json.load",
        side_effect=fake_json_load,
    ):
        QuestionRelevanceGuard().evaluate(
            question="Compare machine learning and deep learning.",
            fact="Traditional machine learning uses manual feature extraction.",
        )

    prompt = captured["messages"][0]["content"].lower()

    assert "either subject" in prompt
    assert "unrelated" in prompt
    assert "different languages" in prompt
    assert "accuracy" in prompt
    assert "precision" in prompt
    assert "recall" in prompt
