from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(max_length=100)
    unit = models.CharField(max_length=64)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=15)
    slug = models.SlugField()
    checkbox_style = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipe_author")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="recipe/")
    text = models.TextField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    ingredients = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient')
    tag = models.ManyToManyField(Tag, related_name='tag')
    cook_time = models.IntegerField()

    def __str__(self):
        return self.title


class Amount(models.Model):
    amount = models.IntegerField()
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following")
