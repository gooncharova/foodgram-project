# from django.conf import settings
# from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
# get_object_or_404, redirect,
from .models import Recipe


def index(request):
    recipe_list = Recipe.objects.order_by("-pub_date").all()
    paginator = Paginator(recipe_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, "paginator": paginator, })
    # "cache_timeout":
    # settings.CACHE_TIME})


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
