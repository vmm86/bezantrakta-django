from django.contrib import admin

from project.decorators import domain_filter
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'is_published', 'domain',)
    list_select_related = ('domain',)

    @domain_filter('domain__slug')
    def get_queryset(self, request):
        return super().get_queryset(request)
