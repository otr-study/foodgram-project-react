from django.contrib import admin

from .models import Ingredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_display_links = ('pk', 'name')


admin.site.register(Ingredient, IngredientAdmin)
