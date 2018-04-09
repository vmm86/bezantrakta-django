from django.contrib import admin
from django.urls import reverse

from project.decorators import queryset_filter
from project.shortcuts import build_absolute_url

from ..models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'is_published', 'domain',)
    list_select_related = ('domain',)
    list_per_page = 10
    search_fields = ('title',)

    def view_on_site(self, obj):
        """Формирование ссылки "Смотреть на сайте"."""
        url = reverse('article:article', args=[obj.slug])
        return build_absolute_url(obj.domain.slug, url)

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        """Фильтрация по выбранному сайту."""
        return super(ArticleAdmin, self).get_queryset(request)
