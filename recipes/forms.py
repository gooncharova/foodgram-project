from django import forms

from django.forms.widgets import CheckboxSelectMultiple
# from django.db import models
# from multiselectfield import MultiSelectFormField

from .models import Tag, Recipe


# class RecipeForm(forms.ModelForm):
#     tags = MultiSelectFormField(choices=TAGS_CHOICES)

#     class Meta:
#         model = Recipe
#         fields = ('title', 'tags', 'ingredients', 'cook_time', 'text', 'image',)

class TagsFilter(forms.Form):
    # published = boolean_check(Tag)
    tag = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=CheckboxSelectMultiple(),
        to_field_name='slug'
    )
    # nameINgredient = forms.CharField(required=False)
    # valueIngredient = forms.IntegerField(required=False)

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'tag', 'cook_time', 'text', 'image')
        # exclude = ('author', 'pub_date')
        widgets = {'tag': forms.CheckboxSelectMultiple(), }
