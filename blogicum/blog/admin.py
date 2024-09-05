from django.utils import timezone

from django.contrib import admin
from django.db.models import Q

from .models import Category, Location, Post, Comment


class PostPublishedListFilter(admin.SimpleListFilter):
    title = ('Опубликовано')
    parameter_name = 'is_published'

    def lookups(self, request, model_admin):
        return [
            ('published', ('Опубликовано')),
            ('not_published', ('Не опубликовано'))
        ]

    def queryset(self, request, queryset):
        if self.value() == 'published':
            return queryset.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
        if self.value() == 'not_published':
            return queryset.filter(
                Q(pub_date__gte=timezone.now())
                | Q(is_published=False)
                | Q(category__is_published=False)
            )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published')
    search_fields = ['title']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_published']
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'post_published', 'is_scheduled']
    list_filter = [PostPublishedListFilter]
    search_fields = ['pk', 'title']

    @admin.display(boolean=True, description='Опубликовано')
    def post_published(self, obj):
        scheduled = self.is_scheduled(obj)
        published = obj.category.is_published and obj.is_published
        return published and scheduled

    @admin.display(boolean=True, description='Запланированно')
    def is_scheduled(self, obj):
        return obj.pub_date <= timezone.now()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['post__id', 'author_username']
