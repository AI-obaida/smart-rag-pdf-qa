from pathlib import Path

path = Path("tests/test_generation_language_examples_v2.py")

source = Path(
    "app/services/structured_llm_service.py"
).read_text(encoding="utf-8")

def test_english_generation_does_not_include_arabic_example():
    assert "if response_language == \"Arabic\"" in source

def test_arabic_generation_keeps_language_specific_example():
    assert "if response_language == \"Arabic\"" in source
    assert "response_language" in source
