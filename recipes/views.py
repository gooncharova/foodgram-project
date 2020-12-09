# from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RecipeForm
from .models import Recipe, User, Follow


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
            return redirect('recipe', username=recipe.author, recipe_id=recipe_id)
    return render(request, 'formChangeRecipe.html', {'form': form, 'recipe': recipe,
                                                     'edit': True})


@login_required
def recipe_delete(request, username, recipe_id):
    author = get_object_or_404(User, username=username)
    recipe = Recipe.objects.filter(author=author, pk=recipe_id)
    if request.user != author:
        return redirect("post", username=recipe.author, pk=recipe_id)
    recipe.delete()
    return redirect("profile", username=author.username)


@login_required
def subscriptions(request):
    return render(request, 'subscriptions.html')


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user, author=author).exists()
    if request.user != author and follow is False:
        follows = Follow.objects.create(user=request.user, author=author)
        follows.save()
    return redirect("subscribes")


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user, author=author)
    following.delete()
    return redirect("subscribes")


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
