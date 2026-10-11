from sqlalchemy import text

from app import db


class RAGService:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def retrieve(self, question: str, document_id: int, top_k: int = 5):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must not be empty")

        if not isinstance(document_id, int) or isinstance(document_id, bool) or document_id < 1:
            raise ValueError("document_id must be a positive integer")

        if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20")

        vector = self.embedding_model.encode(
            ["query: " + question],
            normalize_embeddings=True,
        )[0]

        if len(vector) != 384:
            raise ValueError("embedding must have 384 dimensions")

        vector_text = "[" + ",".join(map(str, vector.tolist())) + "]"

        rows = db.session.execute(
            text("""
                SELECT
                    c.id AS chunk_id,
                    c.document_id,
                    d.filename,
                    c.page_number,
                    c.chunk_text,
                    1 - (
                        c.embedding <=> CAST(:vector AS vector(384))
                    ) AS similarity
                FROM document_chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.document_id = :document_id
                  AND c.embedding IS NOT NULL
                ORDER BY c.embedding <=> CAST(:vector AS vector(384))
                LIMIT :top_k
            """),
            {
                "vector": vector_text,
                "document_id": document_id,
                "top_k": top_k,
            },
        ).mappings().all()

        return [dict(row) for row in rows]
