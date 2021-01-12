from django.shortcuts import get_object_or_404

from .models import Amount, Ingredient, Tag

tag_1 = 'breakfast'
tag_2 = 'lunch'
tag_3 = 'dinner'


def filtering_tags(request):
    if 'filters' in request.GET:
        get_tags = request.GET.getlist('filters')
    else:
        get_tags = [tag_1, tag_2, tag_3]
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
    for item in request.POST.items():
        if 'nameIngredient' in item[0]:
            return None
    return form.add_error(
        'image',
        'Необходимо указать хотя бы один ингредиент для рецепта')


def get_recipe_tags(recipe):
    tag_visible = recipe.tag.all().values_list('title')
    tag_visible = [item for x in tag_visible for item in x]
    return tag_visible
