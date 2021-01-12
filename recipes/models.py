from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    title = models.CharField(max_length=100,
                             verbose_name='Название ингредиента')
    unit = models.CharField(max_length=64, verbose_name='Единица измерения')

    def __str__(self):
        return self.title


class Tag(models.Model):

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    title = models.CharField(max_length=15, verbose_name='Наименование тега')
    slug = models.SlugField(unique=True)
    checkbox_style = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Recipe(models.Model):

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-pub_date']

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    title = models.CharField(max_length=100, verbose_name='Название рецепта')
    image = models.ImageField(upload_to='recipe/', verbose_name='Изображение')
    text = models.TextField(verbose_name='Описание рецепта')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    ingredients = models.ManyToManyField(
        Ingredient, related_name='ingredients', through='Amount',
        through_fields=('recipe', 'ingredient'), verbose_name='Ингредиенты')
    tag = models.ManyToManyField(Tag, related_name='tag', verbose_name='Тег')
    cook_time = models.PositiveIntegerField(verbose_name='Время приготовления')
    favorite = models.ManyToManyField(User, related_name='favorite',
                                      blank=True, verbose_name='Избранное')

    def __str__(self):
        return self.title


class Amount(models.Model):

    class Meta:
        verbose_name = 'количество ингредиента'
        verbose_name_plural = 'количества ингредиента'

    amount = models.IntegerField(verbose_name='Количество ингредиента')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient',
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='amount',
        verbose_name='Рецепт')


class Follow(models.Model):

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [models.UniqueConstraint(fields=['user', 'author'], name='unique follow')]

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Подписан на')


class ShopList(models.Model):

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='buyer',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_to_shop',
                               verbose_name='Рецепт')
