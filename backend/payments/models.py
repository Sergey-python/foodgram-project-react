from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from recipes.models import AmountIngredient, Recipe

User = get_user_model()


class ShopingCart(models.Model):
    """Модель корзины покупок пользователя."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_cart"
    )
    recipes = models.ManyToManyField(Recipe, related_name="shopping_cart")

    def make_file_content(self) -> dict:
        content = (
            AmountIngredient.objects.filter(recipe__in=self.recipes.all())
            .values("ingredient__name")
            .annotate(amount=Sum("amount"))
        )
        return content

    def make_txt_file_name(self) -> str:
        return f"{self.user.get_full_name()}.txt"
