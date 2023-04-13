from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet


class ReadOnlyOrCreateViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet
):
    """
    Вьюсет, поддерживающий ограниченный набор действий.
    Позволяет получить объект, список объектов или создать объект.
    """

    pass
