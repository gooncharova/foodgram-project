from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_recipe, name='new_recipe'),
    path('<str:username>/', views.profile, name='profile'),
    path('recipe/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('recipe/<int:recipe_id>/edit/', views.recipe_edit, name='recipe_edit'),
    path('<str:username>/<int:recipe_id>/delete/', views.recipe_delete, name='recipe_delete'),
    path("<str:username>/follow/", views.profile_follow, name="profile_follow"),
    path("<str:username>/unfollow/", views.profile_unfollow, name="profile_unfollow"),
]
