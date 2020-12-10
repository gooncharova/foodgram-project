# from django.conf import settings
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RecipeForm
from .models import Follow, Recipe, User


def index(request):
    recipe_list = Recipe.objects.order_by('-pub_date').all()
    paginator = Paginator(recipe_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page,
                                          'paginator': paginator, })
    # 'cache_timeout':
    # settings.CACHE_TIME})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipe_author = author.recipe_author.order_by('-pub_date')
    paginator = Paginator(recipe_author, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'author': author, 'page': page,
                                            'paginator': paginator})


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return render(request, 'recipe.html', {'recipe': recipe})


@login_required
def new_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.author = request.user
            new_recipe.save()
            return redirect('index')
    form = RecipeForm()
    return render(request, 'recipe_form.html', {'form': form})


@login_required
def recipe_edit(request, username, recipe_id):
    author = get_object_or_404(User, username=username)
    recipe = get_object_or_404(Recipe, author=author, pk=recipe_id)
    if request.user != author:
        return redirect('recipe', username=recipe.author, recipe_id=recipe_id)
    form = RecipeForm(request.POST or None,
                      files=request.FILES or None, instance=recipe)
    if request.method == 'POST':
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.save()
            return redirect('recipe', username=recipe.author,
                            recipe_id=recipe_id)
    return render(request, 'formChangeRecipe.html', {'form': form,
                                                     'recipe': recipe,
                                                     'edit': True})


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
    paginator = Paginator(following_list, 3)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'subscriptions.html', context)


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
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user, author=author)
    following.delete()
    return redirect('subscriptions')


@login_required
def favorites(request):
    return render(request, 'favorites.html')


@login_required
def shopping_list(request):
    return render(request, 'shopping_list.html')


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
