import re


class QuestionFactConsistencyGuard:
    """Detect explicit mismatches between requested and reported metrics."""

    METRICS = {
        "accuracy": (
            r"\baccuracy\b",
            r"\baccuracies\b",
            r"\baccurate\b",
        ),
        "precision": (
            r"\bprecision\b",
        ),
        "recall": (
            r"\brecall\b",
            r"\u0627\u0644\u0627\u0633\u062a\u0631\u062c\u0627\u0639",
        ),
        "f1": (
            r"\bf1(?:[-\s]?score)?\b",
        ),
    }

    def _mentioned_metrics(self, text: str) -> set[str]:
        return {
            name
            for name, patterns in self.METRICS.items()
            if any(
                re.search(pattern, text, flags=re.IGNORECASE)
                for pattern in patterns
            )
        }

    def _explicitly_unreported(self, fact: str, metric: str) -> bool:
        patterns = self.METRICS[metric]

        for pattern in patterns:
            metric_pattern = pattern.removeprefix(r"\b").removesuffix(r"\b")

            negative_pattern = (
                r"(?:" + metric_pattern + r")"
                r"\s+(?:is|was|has been)\s+"
                r"(?:not reported|not available|not provided|unknown)"
            )

            if re.search(negative_pattern, fact, flags=re.IGNORECASE):
                return True

        return False

    def _requests_metric_value(self, question: str) -> bool:
        english = re.search(
            r"\b(?:what is|what was)\s+the\s+"
            r"(?:\w+\s+){0,3}"
            r"(?:accuracy|precision|recall|f1(?:[-\s]?score)?)\b",
            question,
            flags=re.IGNORECASE,
        )

        arabic = re.search(
            r"\u0645\u0627\s+\u0647\u064a\s+"
            r"\u062f\u0642\u0629\s+"
            r"\u0627\u0644\u0646\u0645\u0648\u0630\u062c"
            r"\s*\(accuracy\)",
            question,
            flags=re.IGNORECASE,
        )

        english_accuracy = re.search(
            r"\bhow\s+accurate\s+is\b",
            question,
            flags=re.IGNORECASE,
        )

        arabic_recall = re.search(
            r"\u0645\u0627\s+\u0646\u0633\u0628\u0629\s+"
            r"\u0627\u0644\u0627\u0633\u062a\u0631\u062c\u0627\u0639",
            question,
        )

        return bool(
            english or arabic or english_accuracy or arabic_recall
        )

    def evaluate(self, question: str, fact: str) -> dict:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must not be empty")

        if not isinstance(fact, str) or not fact.strip():
            raise ValueError("fact must not be empty")

        requested = self._mentioned_metrics(question)
        reported = self._mentioned_metrics(fact)

        if len(requested) != 1 or not reported:
            verdict = "NOT_APPLICABLE"
        elif requested.isdisjoint(reported):
            verdict = (
                "REJECT"
                if self._requests_metric_value(question)
                else "NOT_APPLICABLE"
            )
        elif self._explicitly_unreported(fact, next(iter(requested))):
            verdict = "NOT_APPLICABLE"
        else:
            verdict = "PASS"

        return {
            "verdict": verdict,
            "requested_metrics": sorted(requested),
            "reported_metrics": sorted(reported),
        }
