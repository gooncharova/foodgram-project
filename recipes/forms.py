from django.forms import ModelForm

from .models import Recipe


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'image', 'text', 'ingredients', 'tag', 'cook_time']
        labels = {
            'title': ('Название рецепта'),
            'image': ('Изображение'),
            'text': ('Описание'),
            'ingredients': ('Ингредиенты'),
            'tag': ('Теги'),
            'cook_time': ('Время приготовления')
        }
