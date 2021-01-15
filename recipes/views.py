import io
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .extras import (filtering_tags, get_recipe_tags, recipe_save,
                     validate_ingredients)
from .forms import RecipeForm
from .models import Amount, Follow, Ingredient, Recipe, ShopList, Tag, User


def index(request):
    tags = filtering_tags(request)
    all_recipes = (
        Recipe.objects.all().distinct().filter(tag__in=tags)
    )
    all_tags = Tag.objects.all()
    paginator = Paginator(all_recipes, settings.PER_PAGE_PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'tags': all_tags,
        'cache_timeout': settings.CACHE_TIME,
    }
    return render(request, 'index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    tags = filtering_tags(request)
    all_recipes = author.recipes.distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    paginator = Paginator(all_recipes, settings.PER_PAGE_PAGINATOR)
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
        all_ingredients = Ingredient.objects.filter(
            title__istartswith=keyword).values('title', 'unit')
        data_notice = [{'title': x['title'], 'dimension': x['unit']}
                       for x in all_ingredients]
        return JsonResponse(data_notice, safe=False)
    else:
        all_ingredients = None
        return JsonResponse({'Found': 'None'})


@login_required
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    validate_ingredients(request, form)
    if form.is_valid():
        recipe_save(request, form)
        return redirect('index')
    context = {'form': form}
    return render(request, 'recipe_form.html', context)


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe_view', recipe_id=recipe_id)
    form = RecipeForm(request.POST or None,
                      files=request.FILES or None, instance=recipe)
    validate_ingredients(request, form)
    if form.is_valid():
        recipe.ingredients.remove()
        recipe.amount.all().delete()
        recipe_save(request, form)
        return redirect('recipe', recipe_id)
    recipe_tags = get_recipe_tags(recipe)
    context = {'form': form, 'recipe': recipe, 'recipe_tags': recipe_tags,
               'edit': True}
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
    all_followings = request.user.follower.all()
    context = {'all_followings': all_followings}
    return render(request, 'subscriptions_list.html', context)


@login_required
@require_POST
def profile_follow(request):
    data = json.loads(request.body)
    profile = get_object_or_404(User, id=data['id'])
    if request.user != profile:
        Follow.objects.get_or_create(user=request.user, author=profile)
        return JsonResponse({'success': True})
    else:
        return redirect('index')


@login_required
@require_http_methods(['DELETE'])
def profile_unfollow(request, id):
    profile = get_object_or_404(User, id=id)
    if profile == request.user:
        return redirect('index')
    unfollow = get_object_or_404(Follow, user=request.user, author=profile)
    unfollow.delete()
    return JsonResponse({'success': True})


@login_required
def favorites(request):
    tags = filtering_tags(request)
    all_recipes = Recipe.objects.filter(
        favorite=request.user).distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    context = {'tags': all_tags, 'recipes': all_recipes}
    return render(request, 'favorites.html', context)


@login_required
def add_favorites(request):
    data = json.loads(request.body)
    recipe = get_object_or_404(Recipe, id=data['id'])
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
    all_shoplists = ShopList.objects.all()
    context = {'all_shoplists': all_shoplists}
    return render(request, 'shopping_list.html', context)


@login_required
@require_POST
def add_purchases(request):
    data = json.loads(request.body)
    recipe = get_object_or_404(Recipe, id=data['id'])
    ShopList.objects.get_or_create(user=request.user, recipe=recipe)
    return JsonResponse({'Success': True})


@login_required
@require_http_methods(['GET', 'DELETE'])
def remove_purchases(request, id):
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, id=id)
        purchase = get_object_or_404(
            ShopList, user=request.user, recipe=recipe)
        purchase.delete()
        return JsonResponse({'all': 'done'})
    elif request.method == 'GET':
        user = request.user
        purchase = get_object_or_404(ShopList, user=user, recipe_id=id)
        purchase.delete()
        return redirect('shopping_list')


@login_required
def download_shopping_list_txt(request):
    filename = 'shoplist.txt'
    content = ''
    shoplist_recipe = ShopList.objects.filter(
        user=request.user).values('recipe_id')
    amount = Amount.objects.filter(
        recipe__in=shoplist_recipe
    ).values(
        'ingredient__title', 'ingredient__unit'
    ).annotate(
        Sum('amount')
    )
    for item in amount:
        title = item['ingredient__title']
        unit = item['ingredient__unit']
        amount_sum = item['amount__sum']
        content = content + f'{title} {amount_sum} {unit}\n'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def download_shopping_list_pdf(request):
    filename = 'shoplist.pdf'
    shoplist_recipe = ShopList.objects.filter(
        user=request.user).values('recipe_id')
    amount = Amount.objects.filter(
        recipe__in=shoplist_recipe
    ).values(
        'ingredient__title', 'ingredient__unit'
    ).annotate(
        Sum('amount')
    )
    shoplist_for_pdf = {}
    for item in amount:
        title = item['ingredient__title']
        unit = item['ingredient__unit']
        amount_sum = item['amount__sum']
        shoplist_for_pdf[title] = [amount_sum, unit]
    if not shoplist_recipe.exists():
        return redirect('shopping_list')
    else:
        pdfmetrics.registerFont(TTFont('Font', 'font.ttf'))
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont('Font', 32)
        canvas_x = 60
        canvas_y = 750
        step_down = 20
        p.drawString(150, 800, 'Список покупок')
        p.setFont('Font', 20)
        for key in shoplist_for_pdf.keys():
            title = key
            amount = str(shoplist_for_pdf[key][0])
            unit = shoplist_for_pdf[key][1]
            p.drawString(canvas_x, canvas_y, title +
                         '   '+amount+'   '+unit)
            canvas_y -= step_down
            if canvas_y < 50 and canvas_x < 400:
                canvas_y = 740
                canvas_x = 400
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=filename)
