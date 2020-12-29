from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_recipe, name='new_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('recipe/<int:recipe_id>/edit/', views.recipe_edit,
         name='recipe_edit'),
    path('my_subscriptions/', views.subscriptions, name='subscriptions'),
    path('subscriptions', views.profile_follow, name='follow'),
    path('subscriptions/<int:id>', views.profile_unfollow, name='unfollow'),
    path('favorites_recipe/', views.favorites, name='favorites'),
    path('favorites', views.add_favorites, name='add_favorite'),
    path('favorites/<int:id>', views.remove_favorites, name='remove_favorite'),
    path('shopping_list/', views.shopping_list, name='shopping_list'),
    path('shopping_list/download_txt', views.download_shopping_list_txt,
         name='download_shopping_list_txt'),
    path('shopping_list/download_pdf', views.download_shopping_list_pdf,
         name='download_shopping_list_pdf'),
    path('purchases', views.add_purchases, name='add_purchases'),
    path('purchases/<int:id>', views.remove_purchases, name='remove_purchase'),
    path('ingredients', views.get_ingredients, name='get_ingredients'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:recipe_id>/delete/',
         views.recipe_delete, name='recipe_delete'),
]
