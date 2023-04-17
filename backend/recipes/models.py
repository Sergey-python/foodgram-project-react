from core.models.mixins import UpdateMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тегов рецептов."""

    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class Recipe(UpdateMixin, models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="recipes/", null=True)
    text = models.TextField()
    cooking_time = models.SmallIntegerField(
        validators=(MinValueValidator(settings.MIN_VALUE_COOKING_TIME),),
        error_messages={
            "errors": "Время готовки не может быть менее одной минуты!"
        },
        default=settings.MIN_VALUE_COOKING_TIME,
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name="recipes")

    class Meta:
        ordering = ("-pub_date",)
        constraints = (
            models.CheckConstraint(
                check=models.Q(
                    cooking_time__gte=settings.MIN_VALUE_COOKING_TIME
                ),
                name="min_value_cooking_time",
            ),
        )

    def __str__(self) -> str:
        return self.name


class AmountIngredient(models.Model):
    """Модель, связывающая количество ингредиента и рецепт."""

    amount = models.FloatField(
        validators=(MinValueValidator(settings.MIN_VALUE_AMOUNT),),
        error_messages={"errors": "Количество не может быть отрицательным!"},
        default=settings.MIN_VALUE_AMOUNT,
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.CheckConstraint(
                check=models.Q(amount__gte=settings.MIN_VALUE_AMOUNT),
                name="min_value_amount",
            ),
        )

    def __str__(self) -> str:
        return (
            f"{self.recipe.name} {self.ingredient.name} "
            f"{self.amount} {self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    """Модель избранных рецептов конкретного пользователя."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} {self.recipe.name}"

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "user"), name="unique_recipe_user"
            ),
        )
