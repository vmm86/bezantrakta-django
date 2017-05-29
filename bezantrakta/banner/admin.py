from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from .models import BannerGroup, BannerGroupItem


@admin.register(BannerGroup)
class BannerGroupAdmin(SortableAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'order',)


@admin.register(BannerGroupItem)
class BannerGroupItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    empty_value_display = 'любой'
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'order', 'is_published', 'banner_group', 'domain',)
    radio_fields = {'banner_group': admin.VERTICAL, }
    list_filter = ('domain', 'banner_group',)
