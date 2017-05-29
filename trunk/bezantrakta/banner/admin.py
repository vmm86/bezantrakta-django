from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from .models import BannerGroup, BannerGroupItem


@admin.register(BannerGroup)
class BannerGroupAdmin(SortableAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title',)


@admin.register(BannerGroupItem)
class BannerGroupItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'is_published', 'banner_group', 'domain',)
    radio_fields = {'banner_group': admin.VERTICAL, }
    list_filter = (
        ('domain', RelatedDropdownFilter),
        'banner_group',
    )
