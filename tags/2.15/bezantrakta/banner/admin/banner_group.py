from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from ..models import BannerGroup


@admin.register(BannerGroup)
class BannerGroupAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug',)
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }
