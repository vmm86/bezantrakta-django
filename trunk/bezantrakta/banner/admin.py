from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

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
        ('domain', RelatedDropdownFilter),
        'banner_group',
    )
    list_select_related = ('banner_group', 'domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'banner_group': admin.VERTICAL, }
