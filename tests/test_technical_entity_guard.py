from app.services.technical_entity_guard import TechnicalEntityGuard


def test_rejects_truncated_django():
    guard = TechnicalEntityGuard()
    assert guard.contains_entity(
        source_text="Allowed frameworks: Dja",
        entity="Django",
    ) is False


def test_accepts_complete_django():
    guard = TechnicalEntityGuard()
    assert guard.contains_entity(
        source_text="Allowed frameworks: Django",
        entity="Django",
    ) is True


def test_rejects_truncated_flask():
    guard = TechnicalEntityGuard()
    assert guard.contains_entity(
        source_text="Allowed frameworks: Fla",
        entity="Flask",
    ) is False


def test_accepts_complete_flask():
    guard = TechnicalEntityGuard()
    assert guard.contains_entity(
        source_text="Allowed frameworks: Flask",
        entity="Flask",
    ) is True


def test_rejects_entity_inside_larger_word():
    guard = TechnicalEntityGuard()
    assert guard.contains_entity(
        source_text="The tool is called MyDjangoHelper.",
        entity="Django",
    ) is False


def test_matches_case_insensitively():
    guard = TechnicalEntityGuard()
    assert guard.contains_entity(
        source_text="DJANGO is allowed.",
        entity="Django",
    ) is True


def test_does_not_confuse_frameworks():
    guard = TechnicalEntityGuard()
    assert guard.contains_entity(
        source_text="Allowed frameworks: Django",
        entity="Flask",
    ) is False
