import io
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
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
    paginator = Paginator(all_recipes, 6)
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
    all_recipes = author.recipe_author.distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    paginator = Paginator(all_recipes, 6)
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
    if request.method == 'POST':
        form = RecipeForm(request.POST or None)
        # tags = request.POST.getlist('tag')
        # print(tags)
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
        form = RecipeForm(request.POST or None, instance=recipe)
        validate_ingredients(request, form)
        if form.is_valid():
            recipe.ingredients.remove()
            recipe.recipe_amount.all().delete()
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
def profile_follow(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        profile = get_object_or_404(User, id=data['id'])
        if request.user != profile:
            Follow.objects.get_or_create(user=request.user, author=profile)
            return JsonResponse({'success': True})
        else:
            return redirect('index')


@login_required
def profile_unfollow(request, id):
    if request.method == 'DELETE':
        profile = get_object_or_404(User, id=id)
        if profile == request.user:
            return redirect('index')
        unfollow = get_object_or_404(Follow, user=request.user, author=profile)
        unfollow.delete()
    return JsonResponse({'success': True})


@login_required
def favorites(request):
    tags = filtering_tags(request)
    all_recipes = Recipe.objects.filter(favorite=request.user).distinct().filter(tag__in=tags)
    all_tags = Tag.objects.all()
    context = {"tags": all_tags, "recipes": all_recipes}
    return render(request, "favorites.html", context)


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


@csrf_exempt
@login_required
def add_purchases(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe = get_object_or_404(Recipe, id=data['id'])
        # if not ShopList.objects.filter(user=request.user,
        #                                recipe=recipe).exists():
        ShopList.objects.get_or_create(user=request.user, recipe=recipe)
    return JsonResponse({'Success': True})


@login_required
def remove_purchases(request, id):
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, id=id)
        purchase = get_object_or_404(ShopList, user=request.user, recipe=recipe)
        purchase.delete()
        return JsonResponse({'all': 'done'})
    elif request.method == 'GET':
        user = request.user
        purchase = get_object_or_404(ShopList, user=user, recipe_id=id)
        print(purchase)
        purchase.delete()
        return redirect('shopping_list')


@login_required
def download_shopping_list_txt(request):
    filename = 'shoplist.txt'
    content = ''
    users_recipe = ShopList.objects.filter(user=request.user).values('recipe_id')
    # print(f'users_recipe = {users_recipe}')
    # print('user_values = ', ShopList.objects.filter(user=request.user).values())
    # recipe = [recipe.recipe for recipe in users_recipe]
    # print(f'recipe = {recipe}')
    amount = Amount.objects.filter(
        recipe__in=users_recipe
    ).values(
        'ingredient__title', 'ingredient__unit'
    ).annotate(
        Sum('amount')
    )
    for item in amount:
        title, dimension, amount_sum = item.values()
        content = content + f'{title} {amount_sum} {dimension}\n'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def download_shopping_list_pdf(request):
    filename = 'shoplist.pdf'
    shoplist = ShopList.objects.filter(user=request.user).values()
    dict_pdf = {}
    for item in shoplist:
        recipe = get_object_or_404(Recipe, id=item['recipe_id'])
        for i in recipe.recipe_amount.all():
            # print(dict_pdf[i.ingredient.title])
            # dict_pdf[i.ingredient.title] = [int(i.amount), i.ingredient.unit]
            dict_pdf[i.ingredient.title] = [dict_pdf.get(i.ingredient.title, 0) + int(i.amount), i.ingredient.unit]
            # if i.ingredient.title not in dict_pdf:
            #     dict_pdf[i.ingredient.title] = [
            #         int(i.amount), i.ingredient.unit]
            # else:
            #     dict_pdf[i.ingredient.title][0] += int(i.quantity)
    if not shoplist.exists():
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
        for i in dict_pdf.keys():
            title = i
            amount = str(dict_pdf[i][0])
            unit = dict_pdf[i][1]
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
