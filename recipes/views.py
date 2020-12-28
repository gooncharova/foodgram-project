# from django.conf import settings
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import RecipeForm
# from .extras import get_all_tags, get_filters
from .models import Follow, Recipe, ShopList, Tag, User, Amount, Ingredient
# from django.contrib import messages

# from django.views.decorators.csrf import csrf_protect


def filtered_tags(request):
    if 'filters' in request.GET:
        list_of_tags = request.GET.getlist('filters')
    else:
        list_of_tags = ['breakfast', 'lunch', 'dinner']
    # tag_urls = {}
    # for tag in ['breakfast', 'lunch', 'dinner']:
    #     tag_urls[tag] = get_tag_url(tags, tag)
    filtered_tags = Tag.objects.filter(slug__in=list_of_tags)
    return filtered_tags


# @csrf_protect
def index(request):
    tags = filtered_tags(request)
    recipe_list = Recipe.objects.all().order_by(
        '-pub_date').distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    # return get_filters(self.request, qs)
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page,
                                          'paginator': paginator,
                                          'tags': all_tags})
    # 'cache_timeout':
    # settings.CACHE_TIME})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    tags = filtered_tags(request)
    recipe_list = author.recipe_author.order_by(
        '-pub_date').distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'author': author,
                                            'page': page,
                                            'paginator': paginator,
                                            'tags': all_tags})


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return render(request, 'recipe.html', {'recipe': recipe})


def get_ingredients(request):
    keyword = request.GET.get('query')
    if keyword:
        ingredient_list = Ingredient.objects.filter(
            title__istartswith=keyword).values_list()
        data_notice = [{'title': x[1], 'dimension': x[2]}
                       for x in ingredient_list]
        return JsonResponse(data_notice, safe=False)
    else:
        ingredient_list = None
        return JsonResponse({'Found': "None"})


def recipe_ingredient(request):
    data = {}
    # print(f'data={data}')
    # print(request.POST.items)
    for item in request.POST.items():
        if 'nameIngredient' in item[0]:
            name = item[1]
        if 'valueIngredient' in item[0]:
            value = item[1]
            data[name] = value
    # print(f'data={data}')
    return(data)


@login_required
def new_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        # ingredients = recipe_ingredient(request)
        # print(ingredients)
        tags = request.POST.getlist('tag')
        print(tags)
        ingredients = recipe_ingredient(request)
        print(ingredients)
        if ingredients == {}:
            form.add_error(
            'image',
            'Необходимо указать хотя бы один ингредиент для рецепта')

        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            # recipe.ingredients = ingredients
            print(form.data)
            # recipe.tag = request.POST.getlist('tags')
            recipe.save()
            ingredients = recipe_ingredient(request)
            print(ingredients)
            if ingredients == {}:
                form.add_error(
                'image',
                'Необходимо указать хотя бы один ингредиент для рецепта')
            for item in ingredients:
                Amount.objects.create(
                    recipe=recipe,
                    ingredient=Ingredient.objects.filter(title=item).all()[0],
                    amount=ingredients[item]
                )
            
            form.save_m2m()

            return redirect('index')
    else:
        form = RecipeForm(request.POST or None, files=request.FILES or None)
    all_tags = Tag.objects.all()
    return render(request, 'recipe_form.html', context={'form': form, 'all_tags': all_tags})


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if recipe.author != request.user:
        return HttpResponse('you cannot do it')
    if request.method != 'POST':
        form = RecipeForm(instance=recipe)
    else:
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        if form.is_valid():
            form.save()
            ingredients = recipe_ingredient(request)
            for item in ingredients:
                Amount.objects.create(
                    recipe=recipe,
                    ingredient=Ingredient.objects.filter(title=item).all()[0],
                    amount=ingredients[item]
                )
            return redirect('recipe', recipe_id)
    ingr_dict = recipe.ingredients.all().values()
    print(ingr_dict)
    tag_dict = recipe.tag.all().values()
    tag_visible = []
    for item in tag_dict:
        tag_visible.append(item['title'])
    return render(
            request, 'recipe_form.html', context={'form': form, 'recipe': recipe, 'tag_visible': tag_visible, 'edit': True}
            )


@login_required
def recipe_delete(request, username, recipe_id):
    author = get_object_or_404(User, username=username)
    recipe = Recipe.objects.filter(author=author, pk=recipe_id)
    if request.user != author:
        return redirect('recipe', username=recipe.author, pk=recipe_id)
    recipe.delete()
    return redirect('profile', username=author.username)


@login_required
def subscriptions(request):
    following_list = request.user.follower.all()
    # paginator = Paginator(following_list, 3)
    # page_number = request.GET.get('page')
    # page = paginator.get_page(page_number)
    context = {
        'following_list': following_list,
        # 'paginator': paginator,
    }
    return render(request, 'subscriptions_list.html', context)


@login_required
def profile_follow(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        profile = get_object_or_404(User, id=data['id'])
        following = Follow.objects.filter(
            user=request.user).filter(author=profile)
        if request.user != profile:
            if not following:
                Follow.objects.create(user=request.user, author=profile)
                return JsonResponse({'success': True})
            elif following:
                return redirect('index')
        else:
            return redirect('index')


@login_required
def profile_unfollow(request, id):
    if request.method == 'DELETE':
        profile = get_object_or_404(User, id=id)
        if profile == request.user:
            return redirect('index')
        unfollow = Follow.objects.get(user=request.user, author=profile)
        unfollow.delete()
    return JsonResponse({'success': True})


@login_required
def favorites(request):
    tags = filtered_tags(request)
    recipe_list = Recipe.objects.filter(favorite=request.user).order_by(
        '-pub_date').distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    return render(request, 'favorites.html', {'tags': all_tags,
                                              'recipes': recipe_list})


# @csrf_protect
@login_required
def add_favorites(request):
    data = json.loads(request.body)
    recipe = Recipe.objects.get(id=data['id'])
    recipe.favorite.add(request.user)
    return JsonResponse({'id': request.POST.get('id')})


@login_required
def remove_favorites(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    user = request.user
    user.favorite.remove(recipe)
    return JsonResponse({'id': id})


@login_required
def shopping_list(request):
    shop_list = ShopList.objects.all()
    return render(request, 'shopping_list.html', {'shop_list': shop_list})


@login_required
def add_purchases(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe = Recipe.objects.get(id=data['id'])
        if not ShopList.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            ShopList.objects.create(user=request.user, recipe=recipe)
    return JsonResponse({'Success': True})


@login_required
def remove_purchases(request, id):
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, id=id)
        purchase = ShopList.objects.get(user=request.user, recipe=recipe)
        purchase.delete()
        return JsonResponse({'all': 'done'})
    elif request.method == 'GET':
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        purchase = get_object_or_404(ShopList, user=user, recipe=recipe)
        purchase.delete()
        return redirect('shopping_list')


# def get_ingredients_js(request):
#     text = request.GET.get('query')
#     data = []
#     ingredients = Ingredient.objects.filter(
#         name__icontains=text).all()
#     for ingredient in ingredients:
#         data.append(
#             {'title': ingredient.name, 'dimension': ingredient.description,'units':ingredient.units_of_measurement})
#     return JsonResponse(data, safe=False)


@login_required
def download_shopping_list(request):
    pass


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
