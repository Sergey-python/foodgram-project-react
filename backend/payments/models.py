from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from recipes.models import AmountIngredient

User = get_user_model()


class ShopingCart(models.Model):
    """Модель корзины покупок пользователя."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_ingredients = models.ManyToManyField(AmountIngredient)

    def make_file_content(self) -> dict:
        content = self.amount_ingredients.values("ingredient__name").annotate(
            amount=Sum("amount")
        )
        return content

    def make_txt_file_name(self):
        return self.user.get_full_name() + ".txt"
