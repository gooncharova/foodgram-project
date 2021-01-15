from django.shortcuts import get_object_or_404

from .models import Amount, Ingredient, Tag

BREAKFAST_TAG = 'breakfast'
LUNCH_TAG = 'lunch'
DINNER_TAG = 'dinner'


def filtering_tags(request):
    if 'filters' in request.GET:
        get_tags = request.GET.getlist('filters')
    else:
        get_tags = [BREAKFAST_TAG, LUNCH_TAG, DINNER_TAG]
    filtered_tags = Tag.objects.filter(slug__in=get_tags)
    return filtered_tags


def recipe_save(request, form):
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    data = []
    for item in request.POST.items():
        if 'nameIngredient' in item[0]:
            title = item[1]
        if 'valueIngredient' in item[0]:
            amount = item[1]
        if 'unitsIngredient' in item[0]:
            unit = item[1]
            ing = get_object_or_404(Ingredient, title=title, unit=unit)
            data.append(
                Amount(ingredient=ing, recipe=recipe, amount=amount)
            )
    Amount.objects.bulk_create(data)
    form.save_m2m()


def validate_ingredients(request, form):
    if request.method == 'POST':
        for item in request.POST.items():
            if 'nameIngredient' in item[0]:
                return None
        return form.add_error(
            'image',
            'Необходимо указать хотя бы один ингредиент для рецепта')


def get_recipe_tags(recipe):
    tag_visible = list(recipe.tag.all().values_list('title'))
    return tag_visible
