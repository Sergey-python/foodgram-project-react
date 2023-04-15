from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteView,
    FollowListView,
    FollowView,
    IngredientViewSet,
    RecipeViewSet,
    ShopingCartDownloadView,
    ShopingCartView,
    TagViewSet,
    UserViewSet,
)

router = DefaultRouter()

router.register("users", UserViewSet, basename="user")
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet, basename="recipe")


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "users/subscriptions/",
        FollowListView.as_view(),
    ),
    path("users/<int:id>/subscribe/", FollowView.as_view()),
    path("recipes/<int:id>/favorite/", FavoriteView.as_view()),
    path("recipes/<int:id>/shopping_cart/", ShopingCartView.as_view()),
    path("recipes/download_shopping_cart/", ShopingCartDownloadView.as_view()),
    path("", include(router.urls)),
]
