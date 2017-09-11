from django.contrib import admin
from django.utils.translation import ugettext as _

from project.decorators import queryset_filter

from ..models import TicketServiceSchemeVenueBinder


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
    list_display = ('ticket_service_scheme_title', 'ticket_service_scheme_id',
                    'if_scheme_exists', 'ticket_service',)
    list_filter = (
        ('ticket_service', admin.RelatedOnlyFieldListFilter),
    )
    list_per_page = 10
    readonly_fields = ('ticket_service', 'ticket_service_scheme_id',)

    @queryset_filter('Domain', 'ticket_service__domain__slug')
    def get_queryset(self, request):
        return super(TicketServiceSchemeVenueBinderAdmin, self).get_queryset(request)

    def if_scheme_exists(self, obj):
        """Иконка обозначанет, заполнена ли схема зала."""
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        if obj.scheme != '':
            return _boolean_icon(True)
        else:
            return _boolean_icon(False)
    if_scheme_exists.short_description = _('ticket_service_venue_binder_if_scheme_exists')
