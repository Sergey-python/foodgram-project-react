from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователей."""

    email = models.EmailField(max_length=254, unique=True)


class Follow(models.Model):
    """Модель подписок."""

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follows"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("follower", "following"), name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="cant_follow_yourself",
            ),
        )

    def __str__(self) -> str:
        return f"{self.follower} follower of {self.following}"
