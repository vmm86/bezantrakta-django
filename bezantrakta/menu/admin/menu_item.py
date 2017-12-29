from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from project.decorators import queryset_filter

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'menu', 'domain',)
    list_filter = (
        ('menu', RelatedOnlyFieldDropdownFilter),
    )
    list_select_related = ('menu', 'domain',)
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'menu': admin.VERTICAL, }

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        return super(MenuItemAdmin, self).get_queryset(request)
