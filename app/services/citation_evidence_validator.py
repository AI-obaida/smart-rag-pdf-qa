from __future__ import annotations

from typing import Any


class CitationEvidenceValidator:
    """Measure semantic similarity between a claim and its cited source.

    Similarity is a review signal, not proof of factual support.
    """

    def __init__(self, embedding_model: Any):
        if embedding_model is None:
            raise ValueError("embedding_model is required")
        self.embedding_model = embedding_model

    def evaluate(self, fact: str, source_text: str) -> dict:
        if not isinstance(fact, str) or not fact.strip():
            raise ValueError("fact must not be empty")

        if not isinstance(source_text, str) or not source_text.strip():
            raise ValueError("source_text must not be empty")

        from math import isfinite
        import numpy as np

        vectors = self.embedding_model.encode(
            [
                "query: " + fact.strip(),
                "passage: " + source_text.strip(),
            ],
            convert_to_numpy=True,
        )

        vectors = np.asarray(vectors, dtype=np.float64)

        if vectors.ndim != 2 or vectors.shape[0] != 2:
            raise ValueError("Unexpected embedding shape")

        if not np.all(np.isfinite(vectors)):
            raise ValueError("Embeddings contain non-finite values")

        first, second = vectors
        first_norm = np.linalg.norm(first)
        second_norm = np.linalg.norm(second)

        if first_norm == 0 or second_norm == 0:
            raise ValueError("Embeddings must be nonzero")

        similarity = float(
            np.dot(first, second) / (first_norm * second_norm)
        )

        if not isfinite(similarity):
            raise ValueError("Invalid similarity result")

        return {
            "similarity": round(similarity, 4),
            "method": "embedding_cosine_similarity",
            "verified": False,
        }
