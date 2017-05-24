from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'is_published', 'domain',)
    list_filter = ('domain',)
    # radio_fields = {'domain': admin.VERTICAL}
