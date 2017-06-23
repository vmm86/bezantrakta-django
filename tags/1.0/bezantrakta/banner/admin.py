from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from project.decorators import domain_filter
from .models import BannerGroup, BannerGroupItem


@admin.register(BannerGroup)
class BannerGroupAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title',)
    prepopulated_fields = {
        'slug': ('title',),
    }


@admin.register(BannerGroupItem)
class BannerGroupItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'banner_group', 'domain',)
    list_filter = (
        'banner_group',
    )
    list_select_related = ('banner_group', 'domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'banner_group': admin.VERTICAL, }

    @domain_filter('domain__slug')
    def get_queryset(self, request):
        return super().get_queryset(request)
