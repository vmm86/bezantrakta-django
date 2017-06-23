from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from project.decorators import domain_filter
from .models import Menu, MenuItem


@admin.register(Menu)
class MenuAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title',)
    prepopulated_fields = {
        'slug': ('title',),
    }


@admin.register(MenuItem)
class MenuItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'is_published', 'menu', 'domain',)
    list_filter = (
        'menu',
    )
    list_select_related = ('menu', 'domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'menu': admin.VERTICAL, }

    @domain_filter('domain__slug')
    def get_queryset(self, request):
        return super().get_queryset(request)
