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

        # Check the scope of explicit prohibitions.
        entity_pattern = (
            r"[A-Za-z][A-Za-z0-9+#-]*(?:\.[A-Za-z0-9+#-]+)*"
        )
        separator = r"(?:\s*,\s*(?:or\s+)?|\s+or\s+)"

        prohibition_pattern = (
            r"\b(?:must|shall)\s+not\s+use\s+"
            + r"(" + entity_pattern
            + r"(?:" + separator + entity_pattern + r")*)"
        )

        for sentence in self._sentences(source_text):
            match = re.search(
                prohibition_pattern,
                sentence,
                re.IGNORECASE,
            )

            if not match:
                continue

            prohibited_entities = {
                entity.lower()
                for entity in re.findall(
                    entity_pattern,
                    match.group(1),
                )
                if entity.lower() != "or"
            }

            claim_entities = {
                entity.lower()
                for entity in re.findall(
                    entity_pattern,
                    fact,
                )
            }

            # A combination prohibition is not a blanket ban
            # on every technology mentioned in that combination.
            if re.search(
                r"\bwith\s+" + entity_pattern,
                sentence[match.end():],
                re.IGNORECASE,
            ):
                prohibited_entities = set()

                if (
                    "with" in fact.lower()
                    and all(
                        re.search(
                            r"(?<!\w)" + re.escape(entity) + r"(?!\w)",
                            fact,
                            re.IGNORECASE,
                        )
                        for entity in re.findall(
                            entity_pattern,
                            sentence[match.start():],
                        )
                        if entity.lower() not in {
                            "must", "shall", "not", "use", "with",
                            "students",
                        }
                    )
                ):
                    return {
                        "allowed": False,
                        "reason": "explicit_prohibition_conflict",
                    }

            if prohibited_entities & claim_entities:
                source_subject = re.search(
                    r"^\s*(Students|Teachers|The project)\b",
                    sentence,
                    re.IGNORECASE,
                )
                claim_subject = re.search(
                    r"^\s*(Students|Teachers|The project)\b",
                    fact,
                    re.IGNORECASE,
                )

                if (
                    source_subject
                    and claim_subject
                    and {source_subject.group(1).lower(),
                         claim_subject.group(1).lower()}
                    == {"students", "teachers"}
                ):
                    continue

                return {
                    "allowed": False,
                    "reason": "explicit_prohibition_conflict",
                }

        # A conditional cross-language statement may be
        # uncertain rather than an established contradiction.
        if arabic_must in fact and arabic_use in fact:
            if any(
                re.search(r"\bif\b", sentence, re.IGNORECASE)
                and not re.search(
                    r"\bonly\s+if\b", sentence, re.IGNORECASE
                )
                for sentence in self._sentences(source_text)
            ):
                return {
                    "allowed": True,
                    "reason": "cross_language_conditional_uncertainty",
                }

        # A related mandatory statement with a different subject
        # is uncertain, not an exact match or explicit contradiction.
        if re.search(r"\bthe project\b", fact, re.IGNORECASE):
            claim_entities = set(
                entity.lower()
                for entity in re.findall(
                    r"\b[A-Z][A-Za-z0-9_.+-]*\b", fact
                )
                if entity.lower() not in {"the", "project"}
            )

            for sentence in self._sentences(source_text):
                if not (
                    re.search(r"\bstudents\b", sentence, re.IGNORECASE)
                    and self._matches(sentence, self.STRONG)
                ):
                    continue

                for entity in claim_entities:
                    if re.search(
                        r"(?<!\w)" + re.escape(entity) + r"(?!\w)",
                        sentence,
                        re.IGNORECASE,
                    ):
                        return {
                            "allowed": True,
                            "reason": "different_subject_uncertainty",
                        }

        # A different subject and technical entity do not, by
        # themselves, establish an explicit modality contradiction.
        # Keep the cross-language mandatory-claim policy unchanged.
        if (
            re.search(r"\bthe project\b", fact, re.IGNORECASE)
            and re.search(r"\bmust\b", fact, re.IGNORECASE)
            and not claim_negative
        ):
            for sentence in self._sentences(source_text):
                if (
                    re.search(r"\bstudents\b", sentence, re.IGNORECASE)
                    and self._matches(sentence, self.STRONG)
                    and not self._matches(sentence, self.NEGATION)
                ):
                    return {
                        "allowed": True,
                        "reason": "different_subject_uncertainty",
                    }

        return {
            "allowed": False,
            "reason": "no_matching_source_statement",
        }
