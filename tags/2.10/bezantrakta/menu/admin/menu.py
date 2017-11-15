from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from ..models import Menu


@admin.register(Menu)
class MenuAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug',)
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }
