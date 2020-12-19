# from django.conf import settings
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RecipeForm
# from .extras import get_all_tags, get_filters
from .models import Follow, Recipe, ShopList, Tag, User, Amount, Ingredient
from django.contrib import messages

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


@login_required
def new_recipe(request):
    if request.method != 'POST':
        form = RecipeForm()
    else:
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        i = 1
        ingredients = []
        while request.POST.get(f'nameIngredient_{i}') is not None:
            ingredients.append([request.POST.get(
                f'nameIngredient_{i}'), request.POST.get(f'valueIngredient_{i}')])
            i += 1
        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.author = request.user
            new_recipe = form.save()
            ingredients_dict = {}
            for pair in ingredients:
                name = str(pair[0])
                val = int(pair[1])
                if name not in ingredients_dict:
                    ingredients_dict[name] = val
                else:
                    ingredients_dict[name] += val
            for ingredient in ingredients_dict.keys():
                if Ingredient.objects.filter(title=ingredient).exists():
                    Amount.objects.create(recipe=new_recipe, ingredient=Ingredient.objects.get(
                    title=ingredient), amount=ingredients_dict[ingredient])
                else:
                    messages.error(request, f"{ingredient} нету в базе. сорян. попробуй еще раз.")
                    del ingredients_dict[ingredient]
                    form = RecipeForm(data=request.POST, instance=new_recipe)
                    print(ingredients_dict)
                    context = {'recipe': new_recipe,
                               "ingredients_dict": ingredients_dict,
                               'form': form}
                    return render(request, 'recipe_form.html', context)
            return redirect('index')
    context = {'form': form}
    return render(request, 'recipe_form.html', context)


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return HttpResponse('you cannot do it')
    if request.method != 'POST':
        form = RecipeForm(instance=recipe)
    else:
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe', id)
    context = {'recipe': recipe, 'form': form, 'edit': True}
    return render(request, 'recipe_form.html', context)


@login_required
def recipe_delete(request, username, recipe_id):
    author = get_object_or_404(User, username=username)
    recipe = Recipe.objects.filter(author=author, pk=recipe_id)
    if request.user != author:
        return redirect('post', username=recipe.author, pk=recipe_id)
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


def get_ingredients(request):
    keyword = request.GET.get('query')
    if keyword:
        ingredient_list = Ingredient.objects.filter(
            title__contains=keyword).values_list()
        data_noice = [{'title': x[1], 'dimension': x[2]}
                      for x in ingredient_list]
        return JsonResponse(data_noice, safe=False)
    else:
        ingredient_list = None
        return JsonResponse({'Found': "None"})

@login_required
def download_shopping_list(request):
    pass


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
