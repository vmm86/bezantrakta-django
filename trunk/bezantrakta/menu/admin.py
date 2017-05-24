from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from .models import Menu, MenuItem


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'order',)


@admin.register(MenuItem)
class MenuItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'menu', 'order', 'is_published', 'domain',)
    list_filter = ('domain',)
