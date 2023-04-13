from django.contrib import admin
from django.db.models.aggregates import Count

from .models import AmountIngredient, Ingredient, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "text", "cooking_time", "favorite_count")
    list_filter = ("name", "author", "tags")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        return Recipe.objects.annotate(favorite_count=Count("favorites"))

    def favorite_count(self, obj):
        return obj.favorite_count


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    empty_value_display = "-пусто-"


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(AmountIngredient)
