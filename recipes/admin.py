from django.contrib import admin
from django.db.models import Count

from .models import Amount, Follow, Ingredient, Recipe, ShopList, Tag


class AmountInLine(admin.TabularInline):
    model = Amount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (AmountInLine, )
    filter_horizontal = ('tag',)
    list_display = ('pk', 'title', 'author', 'get_favorite',)
    ordering = ['title', ]
    list_filter = ('title', 'author', 'tag')
    autocomplete_fields = ('ingredients',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_get_favorite=Count('favorite'))

    def get_favorite(self, obj):
        return obj._get_favorite

    get_favorite.short_description = 'В избранном'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit')
    ordering = ['title', ]
    list_filter = ('title',)
    search_fields = ('title', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', )
    search_fields = ('name', )


class AmountAdmin(admin.ModelAdmin):
    list_display = ('amount', 'ingredient', 'recipe', )


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Amount, AmountAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShopList)
