from pathlib import Path


def test_arabic_generation_prompt_requires_natural_language():
    source = Path(
        "app/services/structured_llm_service.py"
    ).read_text(encoding="utf-8")

    assert "Use natural Arabic grammar" in source
    assert "Translate ordinary English verbs into Arabic" in source
    assert "Keep established technical names in English" in source
    assert "Do not invent or alter source facts" in source
