from django.contrib import admin

from .models import Favorite, IngredientRecipe, Recipe, ShoppingCart, TagRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    fields = (
        'name', 'author', 'text', 'image', 'cooking_time', 'get_popularity'
    )
    readonly_fields = ('get_popularity',)
    list_filter = ('name', 'author', 'tags')
    list_display_links = ('pk', 'name')

    @admin.display(description='Popularity')
    def get_popularity(self, obj):
        return obj.favorite.count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_display_links = ('pk', 'user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_display_links = ('pk', 'user', 'recipe')


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'recipe')
    search_fields = ('ingredient', 'recipe')
    list_display_links = ('pk', 'ingredient', 'recipe')


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tag', 'recipe')
    search_fields = ('tag', 'recipe')
    list_display_links = ('pk', 'tag', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
