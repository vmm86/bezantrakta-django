from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'is_published', 'domain',)
    # list_editable = ('is_published',)
    list_filter = ('domain',)
    # radio_fields = {'domain': admin.VERTICAL}

    # def view_domain(self, obj):
    #     return obj.domain

    # view_domain.empty_value_display = 'любой домен'
