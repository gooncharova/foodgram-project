from django.contrib import admin

from .models import Amount, Follow, Ingredient, Recipe, Tag


class AmountInLine(admin.TabularInline):
    model = Amount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (AmountInLine, )
    filter_horizontal = ('tag', )
    list_display = ('pk', 'title', 'author', )
    # 'text', 'pub_date',
    # 'image', 'ingredient', 'tag', 'cook_time')
    search_fields = ('title', )
    list_filter = ('author', 'title', 'tag')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit')
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', )
    list_filter = ('title', 'slug', )
    empty_value_display = '-пусто-'


class AmountAdmin(admin.ModelAdmin):
    list_display = ('amount', 'ingredient', 'recipe', )
    list_filter = ('ingredient', 'recipe', )
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
