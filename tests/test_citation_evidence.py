def test_citation_must_support_claim():
    sources = {
        "S4": (
            "Students must evaluate the performance of their "
            "application and provide the results in a Word "
            "document or another clearly formatted document."
        ),
        "S5": (
            "Accuracy, Precision, Recall, F1-score, "
            "Mean Average Precision (mAP)"
        ),
    }

    claim = (
        "Students must evaluate the performance of their "
        "application and provide the results in a Word "
        "document or another clearly formatted document."
    )

    assert claim in sources["S4"]

    # A source containing only evaluation metrics does not
    # establish the reporting requirement.
    assert claim not in sources["S5"]
