from django import forms
# from django.db import models

from .models import Recipe, Tag


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),
                                          required=True, widget=forms.CheckboxSelectMultiple)
    nameINgredient = forms.CharField(required=False)
    valueIngredient = forms.IntegerField(required=False)

    class Meta:
        model = Recipe
        fields = ['title', 'tags', 'cook_time', 'text', 'image']
        exclude = ('author', 'pub_date', 'ingredients')


# from django.forms import ModelForm

# from .models import Recipe


# class RecipeForm(ModelForm):
#     class Meta:
#         model = Recipe
#         fields = ['title', 'image', 'text', 'ingredients', 'tag', 'cook_time']
#         labels = {
#             'title': ('Название рецепта'),
#             'image': ('Изображение'),
#             'text': ('Описание'),
#             'ingredients': ('Ингредиенты'),
#             'tag': ('Теги'),
#             'cook_time': ('Время приготовления')
#         }
