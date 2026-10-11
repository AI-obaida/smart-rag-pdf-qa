from typing import List, Tuple


class DocumentChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")

        if not isinstance(chunk_overlap, int) or isinstance(chunk_overlap, bool):
            raise ValueError("chunk_overlap must be an integer")

        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError("chunk_overlap must be between 0 and chunk_size - 1")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text_by_page: List[Tuple[int, str]]) -> List[dict]:
        chunks = []
        chunk_id = 1
        step = self.chunk_size - self.chunk_overlap

        for page_num, page_text in text_by_page:
            if not page_text:
                continue

            start = 0

            while start < len(page_text):
                end = min(start + self.chunk_size, len(page_text))

                chunks.append({
                    "page": page_num,
                    "chunk_text": page_text[start:end],
                    "chunk_id": chunk_id,
                })

                chunk_id += 1

                if end == len(page_text):
                    break

                start += step

        return chunks