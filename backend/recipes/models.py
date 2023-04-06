from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Recipe(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    cooking_time = models.SmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class Tag(models.Model):

    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(max_length=20)
    amount = models.SmallIntegerField()

    def __str__(self):
        return self.name