from src.domain.entities.category import Category


def test_create_category() -> None:
    cat = Category.create(name="Sports")
    assert cat.name.value == "Sports"
    assert cat.is_active is True
    assert cat.parent_id is None


def test_deactivate_and_rename() -> None:
    cat = Category.create(name="Sports")
    cat.deactivate()
    assert cat.is_active is False
    cat.rename("Outdoor Sports")
    assert cat.name.value == "Outdoor Sports"
    cat.activate()
    assert cat.is_active is True
