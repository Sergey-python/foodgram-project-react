from django.contrib import admin

from .models import AmountIngredient, Ingredient, Recipe, Tag

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(AmountIngredient)
