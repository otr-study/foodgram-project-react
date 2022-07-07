from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    list_display_links = ('pk', 'username')


class SubscribtionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'subscriber')
    search_fields = ('author', 'subscriber')
    list_display_links = ('pk', 'author', 'subscriber')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscribtionAdmin)
