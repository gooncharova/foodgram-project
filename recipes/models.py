from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(max_length=100)
    unit = models.IntegerField(max_length=15)

     def __str__(self):
        return self.name


class Tag(models.Model):
    title = models.CharField(max_length=15)
    slug = models.SlugField()
    checkbox_style = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Recipe(models.Model):
     class Meta:
        ordering = ['-pub_date']

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="recipe_author")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="recipe/")
    text = models.TextField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name='tag')
    cook_time = models.IntegerField(max_length=10, related_name='cooking_time')

    def __str__(self):
        return self.text


class Amount(models.Model):
    unit = models.IntegerField()
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following")
