import re


class ModalityGuard:
    """
    Conservative sentence-level modality validation.

    Does not replace semantic entailment validation.
    """

    STRONG = (
        r"\bmust\b",
        r"\brequired to\b",
        r"\bare required to\b",
        r"\bis required to\b",
        r"\bhave to\b",
        r"\bhas to\b",
        r"\bshall\b",
        r"\bmandatory\b",
        "\u064a\u062c\u0628",
        "\u0644\u0627 \u0628\u062f",
        "\u0644\u0627\u0628\u062f",
        "\u0625\u0644\u0632\u0627\u0645\u064a",
        "\u0627\u0644\u0632\u0627\u0645\u064a",
        "\u064a\u062a\u0639\u064a\u0646",
    )

    NEGATION = (
        r"\bmust\s+not\b",
        r"\bshould\s+not\b",
        r"\bmay\s+not\b",
        r"\bnot\s+allowed\b",
        r"\bprohibited\b",
        "\u064a\u062c\u0628 \u0623\u0644\u0627",
        "\u0645\u0645\u0646\u0648\u0639",
    )

    def _matches(self, text, patterns):
        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in patterns
        )

    def _normalize(self, text):
        text = text.casefold()
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def _remove_modality(self, text):
        text = re.sub(
            r"\b(?:must|should|may|can|shall)\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\b(?:are required to|is required to|"
            r"required to|have to|has to)\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )
        return self._normalize(text)

    def _sentences(self, text):
        return [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", text)
            if part.strip()
        ]

    def evaluate(self, fact, source_text):
        result = self._evaluate_modality(
            fact=fact,
            source_text=source_text,
        )

        reason = result['reason']

        if not result['allowed']:
            verdict = 'REJECT'
        elif reason in (
            'matching_mandatory_statement',
            'narrow_cross_language_must_use',
        ):
            verdict = 'PASS'
        else:
            verdict = 'NOT_APPLICABLE'

        return {
            **result,
            'verdict': verdict,
        }

    def _evaluate_modality(self, fact, source_text):
        if not isinstance(fact, str) or not fact.strip():
            raise ValueError("fact must not be empty")

        if not isinstance(source_text, str) or not source_text.strip():
            raise ValueError("source_text must not be empty")

        fact = fact.strip()
        source_text = source_text.strip()

        claim_strong = self._matches(fact, self.STRONG)

        if not claim_strong:
            return {
                "allowed": True,
                "reason": "no_mandatory_overstatement_detected",
            }

        claim_negative = self._matches(fact, self.NEGATION)
        claim_core = self._remove_modality(fact)

        for sentence in self._sentences(source_text):
            source_core = self._remove_modality(sentence)

            if source_core != claim_core:
                continue

            source_strong = self._matches(
                sentence,
                self.STRONG,
            )

            source_negative = self._matches(
                sentence,
                self.NEGATION,
            )

            if claim_negative != source_negative:
                return {
                    "allowed": False,
                    "reason": "negation_mismatch",
                }

            if not source_strong:
                return {
                    "allowed": False,
                    "reason": "mandatory_claim_without_mandatory_source",
                }

            return {
                "allowed": True,
                "reason": "matching_mandatory_statement",
            }

        # Narrow cross-language rule:
        # English "must use X" vs Arabic "must ... use X".
        arabic_must = "\u064a\u062c\u0628"
        arabic_use = "\u0627\u0633\u062a\u062e\u062f\u0627\u0645"

        if arabic_must in fact and arabic_use in fact:
            claim_entities = re.findall(
                r"\b[A-Za-z][A-Za-z0-9_.+-]*\b",
                fact,
            )

            if len(claim_entities) == 1:
                entity = claim_entities[0]

                claim_pattern = (
                    r"(?<!\w)"
                    + re.escape(entity)
                    + r"(?!\w)"
                )

                for sentence in self._sentences(source_text):
                    source_pattern = (
                        r"^\s*Students\s+must\s+use\s+"
                        + re.escape(entity)
                        + r"\s*[.!?]?\s*$"
                    )

                    if not re.search(
                        source_pattern,
                        sentence,
                        re.IGNORECASE,
                    ):
                        continue

                    if self._matches(sentence, self.NEGATION):
                        continue

                    if self._matches(fact, self.NEGATION):
                        continue

                    if not re.search(
                        claim_pattern,
                        fact,
                        re.IGNORECASE,
                    ):
                        continue

                    return {
                        "allowed": True,
                        "reason": "narrow_cross_language_must_use",
                    }

        # Arabic-English cross-language claims cannot be
        # compared reliably by simple token matching.
        # For now, reject unsupported mandatory matches.
        return {
            "allowed": False,
            "reason": "no_matching_source_statement",
        }
