from django.conf import settings
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from reportlab.pdfgen import canvas

from .forms import RecipeForm
from .extras import filtering_tags, recipe_save, validate_ingredients, get_recipe_tags
from .models import Amount, Follow, Ingredient, Recipe, ShopList, Tag, User

# from django.views.decorators.csrf import csrf_protect


def index(request):
    tags = filtering_tags(request)
    recipe_list = Recipe.objects.all().order_by(
        '-pub_date').distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator,
               'tags': all_tags, 'cache_timeout': settings.CACHE_TIME}
    return render(request, 'index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    tags = filtering_tags(request)
    recipe_list = author.recipe_author.order_by(
        '-pub_date').distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'author': author, 'page': page, 'paginator': paginator,
               'tags': all_tags, 'cache_timeout': settings.CACHE_TIME}
    return render(request, 'profile.html', context)


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    context = {'recipe': recipe}
    return render(request, 'recipe.html', context)


@login_required
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
        return JsonResponse({'Found': 'None'})


@login_required
def new_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        tags = request.POST.getlist('tag')
        print(tags)
        validate_ingredients(request, form)
        if form.is_valid():
            recipe_save(request, form)
            return redirect('index')
    else:
        form = RecipeForm(request.POST or None)
    context = {'form': form}
    return render(request, 'recipe_form.html', context)


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe_view', recipe_id=recipe_id)
    if request.method != 'POST':
        form = RecipeForm(instance=recipe)
    else:
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        validate_ingredients(request, form)
        if form.is_valid():
            recipe.ingredients.remove()
            recipe.recipe_amount.all().delete()
            recipe_save(request, form)
            return redirect('recipe', recipe_id)
    recipe_tags = get_recipe_tags(recipe)
    context = {'form': form, 'recipe': recipe, 'recipe_tags': recipe_tags, 'edit': True}
    return render(request, 'recipe_form.html', context)


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
    context = {'following_list': following_list}
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
    tags = filtering_tags(request)
    recipe_list = Recipe.objects.filter(favorite=request.user).order_by(
        '-pub_date').distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    context = {'tags': all_tags, 'recipes': recipe_list}
    return render(request, 'favorites.html', context)


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
    context = {'shop_list': shop_list}
    return render(request, 'shopping_list.html', context)


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


@login_required
def download_shopping_list_txt(request):
    filename = 'shoplist.txt'
    content = ''
    users_recipe = ShopList.objects.filter(user=request.user)
    recipe = [recipe.recipe for recipe in users_recipe]
    amount = Amount.objects.filter(
        recipe__in=recipe
    ).values(
        'ingredient__title', 'ingredient__unit'
    ).annotate(
        Sum('amount')
    )
    for a in amount:
        title, dimension, amount_sum = a.values()
        content = content + f'{title} {amount_sum} {dimension}\n'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def download_shopping_list_pdf(request):
    filename = 'shoplist.pdf'
    content = ''
    users_recipe = ShopList.objects.filter(user=request.user)
    recipe = [recipe.recipe for recipe in users_recipe]
    amount = Amount.objects.filter(
        recipe__in=recipe
    ).values(
        'ingredient__title', 'ingredient__unit'
    ).annotate(
        Sum('amount')
    )
    for a in amount:
        title, dimension, amount_sum = a.values()
        content = content + f'{title} {amount_sum} {dimension}\n'
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    # buffer = StringIO()
    p = canvas.Canvas(response)
    p.drawString(100, 100, content)
    p.showPage()
    p.save()
    # pdf = buffer.getvalue()
    # buffer.close()
    # response.write(pdf)
    return response


def page_not_found(request, exception):
    context = {'path': request.path}
    return render(request, 'misc/404.html', context, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
