from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from .models import Menu, MenuItem


@admin.register(Menu)
class MenuAdmin(SortableAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title',)


@admin.register(MenuItem)
class MenuItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'order', 'is_published', 'menu', 'domain',)
    radio_fields = {'menu': admin.VERTICAL, }
    list_filter = (
        ('domain', RelatedDropdownFilter),
        'menu'
    )
