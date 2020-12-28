from django import template

from recipes.models import Follow, ShopList, Recipe, Tag

register = template.Library()


@register.filter(name='get_filter_values')
def get_values(value):
    return value.getlist('filters')


@register.filter(name='get_filter_link')
def get_filter_link(request, tag):
    new_request = request.GET.copy()

    if tag.slug in request.GET.getlist('filters'):
        filters = new_request.getlist('filters')
        filters.remove(tag.slug)
        new_request.setlist('filters', filters)
    else:
        new_request.appendlist('filters', tag.slug)

    return new_request.urlencode()


@register.filter(name='is_following')
def is_following(author, user):
    return Follow.objects.filter(user=user, author=author).exists()


# @register.simple_tag()
# def url_replace(request, page, new_page):
#     query = request.GET.copy()
#     query[page] = new_page
#     return query.urlencode()


@register.filter(name='shopping_recipe')
def shopping_recipe(recipe, user):
    return ShopList.objects.filter(user=user, recipe=recipe).exists()


@register.filter(name='shopping_count')
def shopping_count(request, user_id):
    return ShopList.objects.filter(user=user_id).count()


@register.filter(name='recipe_count')
def recipe_count(request, author):
    author_recipe_count = (Recipe.objects.filter(author=author).count()-3)
    if author_recipe_count <= 0:
        return None
    if author_recipe_count % 10 == 1:
        return f'{author_recipe_count} рецепт'
    if author_recipe_count % 10 in [2, 3, 4] and author_recipe_count not in [12, 13, 14]:
        return f'{author_recipe_count} рецептa'
    else:
        return f'{author_recipe_count} рецептов'


@register.filter(name='tag_colour')
def tag_colour(tag):
    qs = Tag.objects.filter(title=tag).values('checkbox_style')
    return(qs[0]['checkbox_style'])


@register.filter(name='tag_id')
def tag_id(tag):
    # print(Tag.objects.filter(title=tag))
    qs = Tag.objects.filter(title=tag).values('id')
    return(qs[0]['id'])
