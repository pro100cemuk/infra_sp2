from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comments, Genre, Title, User, Review

EMPTY_CONST = '-пусто-'
admin.site.register(User, UserAdmin)
admin.site.register(Review)
admin.site.register(Comments)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('slug', 'name')
    list_filter = ('slug', 'name')
    empty_value_display = EMPTY_CONST


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('slug', 'name')
    list_filter = ('slug', 'name')
    empty_value_display = EMPTY_CONST


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'description',
        'category',
        'year'
    )
    search_fields = ('year', 'category', 'genre', 'name')
    list_filter = ('year', 'category', 'genre')
    empty_value_display = EMPTY_CONST
