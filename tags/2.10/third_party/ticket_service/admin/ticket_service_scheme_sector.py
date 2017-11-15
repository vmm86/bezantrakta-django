from django.contrib import admin
from django.utils.translation import ugettext as _

from project.decorators import queryset_filter

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import TicketServiceSchemeVenueBinder, TicketServiceSchemeSector


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
    list_filter = (
        ('scheme', RelatedOnlyFieldDropdownFilter),
    )
    list_per_page = 20

    @queryset_filter('Domain', 'scheme__ticket_service__domain__slug')
    def get_queryset(self, request):
        return super(TicketServiceSchemeSectorAdmin, self).get_queryset(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """В списке залов выводятся только залы в этом городе."""
        if db_field.name == 'scheme':
            city_filter = request.COOKIES.get('bezantrakta_admin_city', None)
            kwargs['queryset'] = TicketServiceSchemeVenueBinder.objects.filter(
                event_venue__city__slug=city_filter
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def if_sector_exists(self, obj):
        """Иконка обозначает, заполнена ли схема сектора."""
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        return _boolean_icon(True) if obj.sector != '' else _boolean_icon(False)
    if_sector_exists.short_description = _('ticketserviceschemesector_if_sector_exists')
