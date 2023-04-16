from core.models import filters


class RecipeFilter(filters.FilterClass):
    """Фильтр для модели Recipe."""

    author = filters.StringFilterField(filter_field="author__username__in")
    tags = filters.StringFilterField(filter_field="tags__slug__in")
    is_favorited = filters.BooleanFilterField(filter_field="is_favorited__in")
    is_in_shopping_cart = filters.BooleanFilterField(
        filter_field="is_in_shopping_cart__in"
    )

    class Meta:
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")
        many_to_many_fields = ("tags__slug__in",)
