import json
import urllib.request


class SearchQueryTranslator:
    def __init__(
        self,
        model="qwen2.5:3b",
        base_url="http://127.0.0.1:11434",
        timeout=120,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def translate(self, question):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must not be empty")

        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Translate the user's Arabic question into English "
                        "for document search. Preserve its exact meaning, "
                        "requirements, negation, conditions, and named entities. "
                        "Do not answer the question. "
                        "Return only the English translation."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            "options": {
                "temperature": 0,
                "num_predict": 160,
            },
        }

        request = urllib.request.Request(
            self.base_url + "/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=self.timeout,
        ) as response:
            result = json.load(response)

        if result.get("done_reason") != "stop":
            raise ValueError("Translation generation incomplete")

        translation = result["message"]["content"].strip()

        if not translation:
            raise ValueError("Empty translation")

        return translation
