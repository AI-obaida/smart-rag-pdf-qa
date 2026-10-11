from sqlalchemy import text
from app import db


class ChunkExpansionService:
    def expand_forward(
        self,
        document_id: int,
        seed_chunk_ids: list[int],
    ) -> list[dict]:

        if not isinstance(document_id, int) or isinstance(document_id, bool) or document_id < 1:
            raise ValueError("document_id must be positive")

        if not seed_chunk_ids:
            raise ValueError("seed_chunk_ids must not be empty")

        if any(
            not isinstance(chunk_id, int)
            or isinstance(chunk_id, bool)
            or chunk_id < 1
            for chunk_id in seed_chunk_ids
        ):
            raise ValueError("Invalid chunk ID")

        seed_rows = db.session.execute(
            text("""
                SELECT id, chunk_index
                FROM document_chunks
                WHERE document_id = :document_id
                  AND id = ANY(:ids)
            """),
            {
                "document_id": document_id,
                "ids": list(set(seed_chunk_ids)),
            },
        ).mappings().all()

        if len(seed_rows) != len(set(seed_chunk_ids)):
            raise ValueError("Some seed chunks were not found")

        indices = sorted({
            neighbor
            for row in seed_rows
            for neighbor in (
                row["chunk_index"],
                row["chunk_index"] + 1,
            )
        })

        rows = db.session.execute(
            text("""
                SELECT
                    id,
                    document_id,
                    chunk_index,
                    page_number,
                    chunk_text
                FROM document_chunks
                WHERE document_id = :document_id
                  AND chunk_index = ANY(:indices)
                ORDER BY chunk_index
            """),
            {
                "document_id": document_id,
                "indices": indices,
            },
        ).mappings().all()

        seed_indices = {
            row["chunk_index"]: row["page_number"]
            for row in rows
            if row["id"] in seed_chunk_ids
        }

        filtered = []

        for row in rows:
            index = row["chunk_index"]
            page = row["page_number"]

            if index in seed_indices:
                filtered.append(dict(row))
            elif seed_indices.get(index - 1) == page:
                filtered.append(dict(row))

        return filtered
