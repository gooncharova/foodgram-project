from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_recipe, name='new_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('recipe/<int:recipe_id>/edit/', views.recipe_edit,
         name='recipe_edit'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('favorites/', views.favorites, name='favorites'),
    path('shopping_list/', views.shopping_list, name='shopping_list'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:recipe_id>/delete/',
         views.recipe_delete, name='recipe_delete'),
    path('subscriptions', views.profile_follow, name='follow'),
    path('subscriptions/<int:id>', views.profile_unfollow, name='unfollow'),
]
