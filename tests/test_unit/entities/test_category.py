from datetime import datetime, timezone
from uuid import UUID

from expenses_tracker.domain.entities.category import Category


class TestCategory:
    def test_category_creation_success(self):
        name = "Food"
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        color = "#FF0000"
        category = Category(name=name, user_id=user_id, color=color)

        assert category.name == name
        assert category.user_id == user_id
        assert category.color == color
        assert isinstance(category.id, UUID)
        assert category.is_default is False
        assert category.description is None
        assert isinstance(category.created_at, datetime)
        assert isinstance(category.updated_at, datetime)
        assert category.created_at.tzinfo == timezone.utc
        assert category.updated_at.tzinfo == timezone.utc

    def test_category_creation_with_optional_fields(self):
        name = "Transport"
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        color = "#00FF00"
        description = "Transportation expenses"
        is_default = True
        category = Category(
            name=name,
            user_id=user_id,
            color=color,
            description=description,
            is_default=is_default,
        )

        assert category.name == name
        assert category.user_id == user_id
        assert category.color == color
        assert category.description == description
        assert category.is_default == is_default
        assert isinstance(category.id, UUID)
        assert isinstance(category.created_at, datetime)
        assert isinstance(category.updated_at, datetime)
