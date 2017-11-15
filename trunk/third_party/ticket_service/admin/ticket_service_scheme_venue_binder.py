from django.contrib import admin
from django.utils.translation import ugettext as _

from project.decorators import queryset_filter

from ..models import TicketServiceSchemeVenueBinder, TicketServiceSchemeSector


class TicketServiceSchemeSectorInline(admin.TabularInline):
    model = TicketServiceSchemeSector
    extra = 0
    fields = ('ticket_service_sector_title', 'ticket_service_sector_id', 'sector',)
    template = 'admin/tabular_custom.html'


@admin.register(TicketServiceSchemeVenueBinder)
class TicketServiceSchemeVenueBinderAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': ('ticket_service_scheme_title',
                           'ticket_service', 'ticket_service_scheme_id',
                           'event_venue', 'scheme')
            }
        ),
    )
    inlines = (TicketServiceSchemeSectorInline,)
    list_display = ('ticket_service_scheme_title', 'ticket_service_scheme_id',
                    'if_scheme_exists', 'if_sectors_exist', 'ticket_service',)
    list_filter = (
        ('ticket_service', admin.RelatedOnlyFieldListFilter),
    )
    list_per_page = 20
    readonly_fields = ('ticket_service', 'ticket_service_scheme_id',)

    @queryset_filter('Domain', 'ticket_service__domain__slug')
    def get_queryset(self, request):
        return super(TicketServiceSchemeVenueBinderAdmin, self).get_queryset(request)

    def if_scheme_exists(self, obj):
        """Иконка обозначает, заполнена ли схема зала."""
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        return _boolean_icon(True) if obj.scheme != '' else _boolean_icon(False)
    if_scheme_exists.short_description = _('ticketservicevenuebinder_if_scheme_exists')

    def if_sectors_exist(self, obj):
        """Иконка обозначанет, добавлены ли связанные со схемой секторы."""
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        return _boolean_icon(True) if obj.scheme_sectors.count() > 0 else _boolean_icon(False)
    if_sectors_exist.short_description = _('ticketservicevenuebinder_if_sectors_exist')
