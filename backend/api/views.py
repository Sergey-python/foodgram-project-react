from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Exists, OuterRef
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from downloadapp.utils import DownloadFile
from payments.models import ShopingCart
from recipes.models import Favorite, Ingredient, Recipe, Tag
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Follow

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateUpdateDestroySerializer,
    RecipeListOrRetrieveSerializer,
    SetPasswordSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .viewsets import ReadOnlyOrCreateViewSet

User = get_user_model()


class UserViewSet(ReadOnlyOrCreateViewSet):
    """
    Вьюсет модели User.
    Поддерживает полный набор действий.
    """

    permission_classes = (AllowAny,)

    def get_queryset(self):
        if self.action == "subscriptions":
            return User.objects.filter(followers__follower=self.request.user)
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        if self.action == "set_password":
            return SetPasswordSerializer
        if self.action == "subscriptions":
            return FollowSerializer
        return UserSerializer

    def _get_request_user(self):
        """Метод получения пользователя из объекта request."""
        return self.request.user

    @action(("get",), detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request):
        """
        Метод, предоставляющий эндпоинт /me/.
        По нему можно получить пользовательскую информацию.
        """
        self.get_object = self._get_request_user
        return self.retrieve(request)

    @action(("post",), detail=False, permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """
        Метод, предоставляющий эндпоинт /set_password/.
        По нему можно обновить пароль.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(("get",), detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """
        Метод, предоставляющий эндпоинт /subscriptions/.
        По нему можно получить список пользователей, на которых
        подписан текущий пользователь.
        """
        return self.list(request)


class FollowView(APIView):
    """
    API класс-контроллер.
    Поддерживает типы запросов: post, delete.
    Предназначен для создания и удаления подписки.
    """

    def post(self, request, id):
        following_user = get_object_or_404(User, id=id)
        try:
            Follow.objects.create(
                follower=request.user, following=following_user
            )
        except IntegrityError:
            raise ParseError({"errors": "Нельзя подписаться!"})
        serializer = FollowSerializer(following_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        following_user = get_object_or_404(User, id=id)
        try:
            follow = Follow.objects.get(
                follower=request.user, following=following_user
            )
        except ObjectDoesNotExist:
            raise ParseError(
                {"errors": "Вы не подписаны на этого пользователя!"}
            )

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    """
    Вьюсет модели Tag.
    Поддерживает ограниченный набор действий: list, retrive.
    Предназначен для получения тегов.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Вьюсет модели Ingredient.
    Поддерживает ограниченный набор действий: list, retrive.
    Предназначен для получения ингредиентов.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ("name",)


class RecipeViewSet(ModelViewSet):
    """
    Вьюсет модели Recipe.
    Поддерживает полный набор действий.
    """

    permission_classes = (IsAuthorOrReadOnly,)
    custom_filter = RecipeFilter()

    def filter_queryset(self, queryset):
        query_params = self.request.query_params
        filter_fields = self.custom_filter.get_filter_fields(query_params)
        return queryset.filter(**filter_fields).distinct()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            user = None
        return (
            Recipe.objects.select_related("author")
            .prefetch_related("ingredients", "tags")
            .annotate(
                is_in_shopping_cart=Exists(
                    ShopingCart.objects.filter(
                        user=self.request.user, recipes=OuterRef("pk")
                    )
                ),
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=self.request.user, recipe=OuterRef("pk")
                    )
                ),
            )
        )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeListOrRetrieveSerializer
        return RecipeCreateUpdateDestroySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance = self.get_queryset().get(id=instance.id)
        serializer = RecipeListOrRetrieveSerializer(
            instance, context={"request": request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class FavoriteView(APIView):
    """
    API класс-контроллер.
    Поддерживает типы запросов: post, delete.
    Предназначен для добавления и удаления рецепта из списка избранного.
    """

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        try:
            Favorite.objects.create(recipe=recipe, user=request.user)
        except IntegrityError:
            raise ParseError({"errors": "Рецепт уже в избранном!"})
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        try:
            favorite = Favorite.objects.get(recipe=recipe, user=request.user)
        except ObjectDoesNotExist:
            raise ParseError({"errors": "Рецепт не в избранном!"})

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopingCartView(APIView):
    """
    API класс-контроллер.
    Поддерживает типы запросов: post, delete.
    Предназначен для добавления и удаления рецепта из корзины покупок.
    """

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        cart, created = ShopingCart.objects.get_or_create(user=request.user)

        if recipe in cart.recipes.all():
            raise ParseError({"errors": "Рецепт уже добавлен в корзину!"})

        cart.recipes.add(recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        cart = get_object_or_404(ShopingCart, user=request.user)

        if recipe not in cart.recipes.all():
            raise ParseError({"errors": "Рецепта нет в корзине!"})

        cart.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopingCartDownloadView(APIView):
    """
    API класс-контроллер.
    Поддерживает типы запросов: get.
    Предназначен для скачивания файла со списком ингредиентов из корзины.
    """

    def get(self, request):
        user_cart = get_object_or_404(ShopingCart, user=request.user)
        content = user_cart.make_file_content()
        file_name = user_cart.make_txt_file_name()

        file = DownloadFile(file_name, content)
        return file.download_file()
