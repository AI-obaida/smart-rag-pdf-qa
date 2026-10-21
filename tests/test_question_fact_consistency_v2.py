import pytest

from app.services.question_fact_consistency_guard import (
    QuestionFactConsistencyGuard,
)


@pytest.mark.parametrize(
    "question,fact,expected",
    [
        (
            "What is the model accuracy?",
            "The model accuracy is 87.5 percent.",
            "PASS",
        ),
        (
            "What is the model accuracy?",
            "The model recall is 92 percent.",
            "REJECT",
        ),
        (
            "What is the model recall?",
            "The model accuracy is 87.5 percent.",
            "REJECT",
        ),
        (
            "What is the model precision?",
            "The model precision is 91 percent.",
            "PASS",
        ),
        (
            "What is the model F1-score?",
            "The model recall is 92 percent.",
            "REJECT",
        ),
        (
            "What is the difference between machine learning "
            "and deep learning?",
            "Deep learning uses multiple layers.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the model accuracy?",
            "The planets orbit the Sun.",
            "NOT_APPLICABLE",
        ),
    ],
)
def test_metric_consistency(question, fact, expected):
    guard = QuestionFactConsistencyGuard()

    result = guard.evaluate(question=question, fact=fact)

    assert result["verdict"] == expected


def test_rejects_empty_question():
    guard = QuestionFactConsistencyGuard()

    with pytest.raises(ValueError):
        guard.evaluate("", "The model accuracy is 90 percent.")


def test_rejects_empty_fact():
    guard = QuestionFactConsistencyGuard()

    with pytest.raises(ValueError):
        guard.evaluate("What is the model accuracy?", "")


@pytest.mark.parametrize(
    "question,fact,expected",
    [
        (
            "\u0645\u0627 \u0647\u064a \u062f\u0642\u0629 "
            "\u0627\u0644\u0646\u0645\u0648\u0630\u062c "
            "(Accuracy)\u061f",
            "The model recall is 92 percent.",
            "REJECT",
        ),
        (
            "What is the model accuracy?",
            "Accuracy is 87 percent and recall is 92 percent.",
            "PASS",
        ),
        (
            "Compare accuracy and recall.",
            "Accuracy is 87 percent.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the difference between machine learning "
            "and deep learning?",
            "Deep learning uses multiple neural network layers.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the model accuracy?",
            "The accuracy is not reported, but recall is 92 percent.",
            "NOT_APPLICABLE",
        ),
    ],
)
def test_metric_consistency_edge_cases(question, fact, expected):
    guard = QuestionFactConsistencyGuard()
    result = guard.evaluate(question=question, fact=fact)
    assert result["verdict"] == expected


@pytest.mark.parametrize(
    "question,fact,expected",
    [
        (
            "What is accuracy?",
            "Recall measures the proportion of actual positives found.",
            "NOT_APPLICABLE",
        ),
        (
            "Explain accuracy and recall.",
            "Recall measures how many actual positives are identified.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the model accuracy?",
            "The model achieved 87 percent correct predictions.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the model accuracy?",
            "Accuracy was not provided in the evaluation.",
            "NOT_APPLICABLE",
        ),
        (
            "What is the model accuracy?",
            "The reported recall was 92 percent.",
            "REJECT",
        ),
    ],
)
def test_metric_guard_safety_cases(question, fact, expected):
    guard = QuestionFactConsistencyGuard()
    result = guard.evaluate(question=question, fact=fact)
    assert result["verdict"] == expected
