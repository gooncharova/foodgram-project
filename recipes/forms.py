from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from .models import Recipe, Tag


class TagsFilter(forms.Form):
    tag = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=CheckboxSelectMultiple(),
        to_field_name='slug'
    )


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ('title', 'tag', 'cook_time', 'text', 'image')
        widgets = {'tag': forms.CheckboxSelectMultiple(), }
