import math

from sqlalchemy import text

from app.services.document_chunking import DocumentChunker


class DocumentIndexingService:
    EMBEDDING_DIMENSIONS = 384

    def __init__(self, embedding_model):
        if embedding_model is None:
            raise ValueError("embedding_model is required")

        self.embedding_model = embedding_model
        self.chunker = DocumentChunker(
            chunk_size=1000,
            chunk_overlap=200,
        )

    def prepare_chunks(self, pages):
        chunks = self.chunker.chunk_text(pages)

        if not chunks:
            return []

        passages = [
            "passage: " + chunk["chunk_text"]
            for chunk in chunks
        ]

        embeddings = self.embedding_model.encode(passages)

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Embedding count does not match chunk count"
            )

        prepared = []

        for chunk, embedding in zip(chunks, embeddings):
            vector = [float(value) for value in embedding]

            if len(vector) != self.EMBEDDING_DIMENSIONS:
                raise ValueError(
                    "Embedding must have 384 dimensions"
                )

            if not all(math.isfinite(value) for value in vector):
                raise ValueError(
                    "Embedding contains non-finite values"
                )

            prepared.append({
                "page_number": chunk["page"],
                "chunk_index": chunk["chunk_id"],
                "chunk_text": chunk["chunk_text"],
                "embedding": vector,
            })

        return prepared

    def store_chunks(self, document_id, chunks, session):
        if (
            not isinstance(document_id, int)
            or isinstance(document_id, bool)
            or document_id < 1
        ):
            raise ValueError("document_id must be a positive integer")

        if session is None:
            raise ValueError("session is required")

        statement = text("""
            INSERT INTO document_chunks (
                document_id,
                page_number,
                chunk_index,
                chunk_text,
                embedding
            )
            VALUES (
                :document_id,
                :page_number,
                :chunk_index,
                :chunk_text,
                CAST(:embedding AS vector(384))
            )
            ON CONFLICT (document_id, chunk_index)
            DO UPDATE SET
                page_number = EXCLUDED.page_number,
                chunk_text = EXCLUDED.chunk_text,
                embedding = EXCLUDED.embedding
        """)

        for chunk in chunks:
            vector = [float(value) for value in chunk["embedding"]]

            if len(vector) != self.EMBEDDING_DIMENSIONS:
                raise ValueError("Embedding must have 384 dimensions")

            if not all(math.isfinite(value) for value in vector):
                raise ValueError("Embedding contains non-finite values")

            vector_literal = "[" + ",".join(
                str(value) for value in vector
            ) + "]"

            session.execute(
                statement,
                {
                    "document_id": document_id,
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "chunk_text": chunk["chunk_text"],
                    "embedding": vector_literal,
                },
            )
