import json
import urllib.request


class LLMService:
    def __init__(
        self,
        model="qwen2.5:3b",
        base_url="http://127.0.0.1:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, question: str, chunks: list[dict]):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must not be empty")

        if not chunks:
            raise ValueError("chunks must not be empty")

        context_parts = []

        for index, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {index} | "
                f"File: {chunk['filename']} | "
                f"Page: {chunk['page_number']}]\n"
                f"{chunk['chunk_text']}"
            )

        context = "\n\n".join(context_parts)

        system_prompt = (
            "You are an Arabic PDF question-answering assistant. "
            "Answer in clear Arabic. "
            "Use ONLY information supported by the provided context. "
            "Cite the page number for every factual claim using "
            "the format (page X). "
            "Do not cite pages absent from the provided context. "
            "Do not invent information. "
            "If the context is insufficient, say so."
        )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        f"DOCUMENT CONTEXT:\n{context}\n\n"
                        f"QUESTION:\n{question}"
                    ),
                },
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 800,
            },
        }

        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=300,
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        answer = (
            (data.get("message") or {})
            .get("content", "")
            .strip()
        )

        if data.get("done_reason") != "stop" or not answer:
            raise RuntimeError(
                "LLM did not produce a complete answer"
            )

        return answer
