from app.services.question_fact_consistency_guard import (
    QuestionFactConsistencyGuard,
)


def test_recall_question_rejects_accuracy_fact():
    guard = QuestionFactConsistencyGuard()

    result = guard.evaluate(
        question="What is the recall of the model?",
        fact="The model accuracy is 95 percent.",
    )

    assert result["verdict"] == "REJECT"


def test_recall_question_accepts_recall_fact():
    guard = QuestionFactConsistencyGuard()

    result = guard.evaluate(
        question="What is the recall of the model?",
        fact="The model recall is 82 percent.",
    )

    assert result["verdict"] == "PASS"
