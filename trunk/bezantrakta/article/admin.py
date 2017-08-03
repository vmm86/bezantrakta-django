from django.contrib import admin

from project.decorators import queryset_filter
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'is_published', 'domain',)
    list_select_related = ('domain',)
    list_per_page = 10

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        return super(ArticleAdmin, self).get_queryset(request)
