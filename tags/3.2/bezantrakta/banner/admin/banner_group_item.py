from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from project.decorators import queryset_filter

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import BannerGroupItem


@admin.register(BannerGroupItem)
class BannerGroupItemAdmin(SortableAdminMixin, admin.ModelAdmin):
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
        return super(BannerGroupItemAdmin, self).get_queryset(request)