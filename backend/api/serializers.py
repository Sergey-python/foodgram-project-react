import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from django.http import Http404
from django.shortcuts import get_object_or_404
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .mixins import MixinPassValidation

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели User.
    Предназначен для вывода информации о пользователях.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user

        if not user.is_authenticated:
            return False

        user_follow = user.follows.filter(following=obj)
        return user_follow.exists()


class UserRegistrationSerializer(
    MixinPassValidation, serializers.ModelSerializer
):
    """
    Сериализатор модели User.
    Предназначен для регистрации пользователей.
    """

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")
        self.validate_user_password(
            password_value=password, password_field="password", user=user
        )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SetPasswordSerializer(MixinPassValidation, serializers.Serializer):
    """
    Сериализатор, предназначенный для сброса паролей пользователей.
    """

    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate_new_password(self, value):
        user = self.context["request"].user
        self.validate_user_password(
            password_value=value, password_field="new_password", user=user
        )
        return value

    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if not is_password_valid:
            raise serializers.ValidationError("invalid_password")
        return value


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipe.
    Предназначен для вывода неполной информации о рецептах.
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели User.
    Предназначен для вывода информации о пользователях и их рецептах,
    на которых подписан текущий авторизованный пользователь.
    """

    is_subscribed = serializers.BooleanField(default=True)
    recipes = ShortRecipeSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Tag.
    Предназначен для вывода информации о тегах.
    """

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    Предназначен для вывода информации об ингредиентах.
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("name", "measurement_unit")


class AmountIngredientSerializer(serializers.Serializer):
    """
    Сериализатор, предназначенный для создании записи о количестве ингредиента.
    Используется, как вложенный для сериализатора
    RecipeCreateUpdateDestroySerializer.
    """

    id = serializers.IntegerField()
    amount = serializers.FloatField()

    def validate_id(self, value):
        try:
            get_object_or_404(Ingredient, id=value)
        except Http404:
            raise ValidationError({"errors": "Такого ингредиента нет!"})
        return value

    def validate_amount(self, value):
        if value < settings.MIN_VALUE_AMOUNT:
            raise ValidationError(
                {"errors": "Количество не может быть отрицательным!"}
            )
        return value


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class RecipeListOrRetrieveSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipe.
    Предназначен для вывода информации о рецептах.
    """

    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer()
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "ingredients",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
            "pub_date",
        )

    def get_ingredients(self, obj):
        ingredients = []
        for ingredient in obj.ingredients.all():
            ingredient_json = {
                "id": ingredient.ingredient.id,
                "name": ingredient.ingredient.name,
                "measurement_unit": ingredient.ingredient.measurement_unit,
                "amount": ingredient.amount,
            }
            ingredients.append(ingredient_json)
        return ingredients


class RecipeCreateUpdateDestroySerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Reicpe.
    Предназначен для создания, изменения и удаления рецепта.
    """

    ingredients = AmountIngredientSerializer(many=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ("id",)

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        new_recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            new_recipe.tags.add(tag)

        for ingredient in ingredients:
            amount = ingredient["amount"]
            ingredient = Ingredient.objects.get(id=ingredient["id"])

            AmountIngredient.objects.create(
                amount=amount,
                recipe=new_recipe,
                ingredient=ingredient,
            )
        return new_recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        instance.update(**validated_data)
        instance.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient["amount"]
            ingredient = Ingredient.objects.get(id=ingredient["id"])
            AmountIngredient.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient,
                defaults={"amount": amount},
            )
        return instance
