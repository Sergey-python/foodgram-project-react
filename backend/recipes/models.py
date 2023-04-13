from core.models.mixins import UpdateMixin
from django.contrib.auth import get_user_model
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
    cooking_time = models.FloatField()
    pub_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name="recipes")

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self) -> str:
        return self.name


class AmountIngredient(models.Model):
    """Модель, связывающая количество ингредиента и рецепт."""

    amount = models.FloatField()
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)


class Favorite(models.Model):
    """Модель избранных рецептов конкретного пользователя."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"], name="unique_recipe_user"
            ),
        ]
