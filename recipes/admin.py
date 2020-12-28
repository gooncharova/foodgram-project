from django.contrib import admin

from .models import Amount, Follow, Ingredient, Recipe, ShopList, Tag


class AmountInLine(admin.TabularInline):
    model = Amount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (AmountInLine, )
    # filter_horizontal = ('tag', 'ingredients',)
    list_display = ('pk', 'title', 'author', )
    ordering = ['title', ]
    list_filter = ('title',)
    autocomplete_fields = ('ingredients',)
    empty_value_display = '-пусто-'

    # def count_favorited(self, obj):
    #     count = Favorite.objects.filter(recipe=obj).count()
    #     return count


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit')
    ordering = ['title', ]
    list_filter = ('title',)
    search_fields = ('title', )
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


class AmountAdmin(admin.ModelAdmin):
    list_display = ('amount', 'ingredient', 'recipe', )
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Amount, AmountAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShopList)
