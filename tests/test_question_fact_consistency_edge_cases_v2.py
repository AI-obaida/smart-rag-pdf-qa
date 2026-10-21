import pytest

from app.services.question_fact_consistency_guard import (
    QuestionFactConsistencyGuard,
)


@pytest.mark.parametrize(
    "question,fact,expected",
    [
        (
            "What is the accuracy of the model?",
            "The model accuracy is not reported.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the recall of the model?",
            "The model recall is unknown.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the accuracy of the model?",
            "The model accuracy is discussed but no value is given.",
            "PASS",
        ),
        (
            "What are the accuracy and recall of the model?",
            "The model precision is 91 percent.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the accuracy of the model?",
            "The model accuracy is 95 percent and recall is 82 percent.",
            "PASS",
        ),
        (
            "What is the accuracy of the model?",
            "The model recall is 82 percent; accuracy was not reported.",
            "NOT_APPLICABLE",
        ),
    ],
)
def test_metric_consistency_edge_cases(question, fact, expected):
    guard = QuestionFactConsistencyGuard()

    result = guard.evaluate(question=question, fact=fact)

    assert result["verdict"] == expected
