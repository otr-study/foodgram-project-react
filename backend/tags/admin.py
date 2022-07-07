import imp

from django.contrib import admin

from .models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    search_fields = ('name',)
    list_display_links = ('pk', 'name')


admin.site.register(Tag, TagAdmin)
