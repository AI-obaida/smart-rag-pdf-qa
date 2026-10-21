import pytest

from app.services.question_fact_consistency_guard import (
    QuestionFactConsistencyGuard,
)


@pytest.mark.parametrize(
    "question,fact,expected",
    [
        (
            "What is the recall of the model?",
            "The model accuracy is 95 percent.",
            "REJECT",
        ),
        (
            "What is the accuracy of the model?",
            "The model precision is 91 percent.",
            "REJECT",
        ),
        (
            "How accurate is the model?",
            "The model recall is 82 percent.",
            "REJECT",
        ),
        (
            "\u0645\u0627 \u0646\u0633\u0628\u0629 "
            "\u0627\u0644\u0627\u0633\u062a\u0631\u062c\u0627\u0639\u061f",
            "The model accuracy is 95 percent.",
            "REJECT",
        ),
        (
            "What is the accuracy of the model?",
            "The model accuracy is 95 percent.",
            "PASS",
        ),
        (
            "What is the recall of the model?",
            "The model recall was not reported.",
            "NOT_APPLICABLE",
        ),
    ],
)
def test_metric_consistency_extended(question, fact, expected):
    guard = QuestionFactConsistencyGuard()

    result = guard.evaluate(
        question=question,
        fact=fact,
    )

    assert result["verdict"] == expected
