from django.contrib import admin
from django.utils.translation import ugettext as _

from project.decorators import queryset_filter

from ..models import TicketServiceSchemeSector


@admin.register(TicketServiceSchemeSector)
class TicketServiceSchemeSectorAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': ('ticket_service_sector_id', 'ticket_service_sector_title',
                           'scheme', 'sector',)
            }
        ),
    )
    list_display = ('ticket_service_sector_title', 'ticket_service_sector_id',
                    'if_sector_exists', 'scheme',)
    list_per_page = 20

    @queryset_filter('Domain', 'scheme__ticket_service__domain__slug')
    def get_queryset(self, request):
        return super(TicketServiceSchemeSectorAdmin, self).get_queryset(request)

    def if_sector_exists(self, obj):
        """Иконка обозначает, заполнена ли схема сектора."""
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        if obj.sector != '':
            return _boolean_icon(True)
        else:
            return _boolean_icon(False)
    if_sector_exists.short_description = _('ticketserviceschemesector_if_sector_exists')
