from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'is_published', 'domain',)
    list_select_related = ('domain',)
    list_filter = (
        ('domain', RelatedDropdownFilter),
    )
