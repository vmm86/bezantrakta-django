from django.contrib import admin
from django.utils.translation import ugettext as _

from adminsortable2.admin import SortableAdminMixin

from project.decorators import queryset_filter

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import BannerGroupItem


@admin.register(BannerGroupItem)
class BannerGroupItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': ('title', 'slug', 'img',),
            }
        ),
        (
            None,
            {
                'fields': ('href',),
                'classes': ('help_text',),
                'description': _('bannergroupitem_href_help_text'),
            }
        ),
        (
            None,
            {
                'fields': ('is_published', 'banner_group', 'domain',),
            }
        )
    )
    list_display = ('title', 'slug', 'is_published', 'banner_group', 'domain',)
    list_filter = (
        ('banner_group', RelatedOnlyFieldDropdownFilter),
    )
    list_select_related = ('banner_group', 'domain',)
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'banner_group': admin.VERTICAL, }

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        """Фильтрация по выбранному сайту."""
        return super(BannerGroupItemAdmin, self).get_queryset(request)
