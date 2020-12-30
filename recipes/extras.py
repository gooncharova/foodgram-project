from .models import Amount, Ingredient, Tag


def filtering_tags(request):
    if 'filters' in request.GET:
        list_of_tags = request.GET.getlist('filters')
    else:
        list_of_tags = ['breakfast', 'lunch', 'dinner']
    filtered_tags = Tag.objects.filter(slug__in=list_of_tags)
    return filtered_tags


def recipe_save(request, form):
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    data = []
    print(request.POST.items)
    for item in request.POST.items():
        if 'nameIngredient' in item[0]:
            title = item[1]
        if 'valueIngredient' in item[0]:
            amount = item[1]
        if 'unitsIngredient' in item[0]:
            unit = item[1]
            ing = Ingredient.objects.get(title=title, unit=unit)
            data.append(
                Amount(ingredient=ing, recipe=recipe, amount=amount)
            )
    Amount.objects.bulk_create(data)
    form.save_m2m()


def validate_ingredients(request, form):
    for item in request.POST.items():
        if 'nameIngredient' in item[0]:
            return None
    print('error')
    return form.add_error(
        'image',
        'Необходимо указать хотя бы один ингредиент для рецепта')


def get_recipe_tags(recipe):
    tag_dict = recipe.tag.all().values()
    tag_visible = []
    for item in tag_dict:
        tag_visible.append(item['title'])
    return tag_visible
