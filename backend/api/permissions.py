from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Permission предоставляющий ограниченный доступ.
    Для чтения любым пользователям.
    Для создания, изменения и удаления только автору.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user == obj.author
