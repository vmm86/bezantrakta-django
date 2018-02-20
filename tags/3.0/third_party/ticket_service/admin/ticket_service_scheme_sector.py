from django.contrib import admin
from django.utils.translation import ugettext as _

from project.cache import cache_factory
from project.decorators import queryset_filter

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import TicketServiceSchemeVenueBinder, TicketServiceSchemeSector


@admin.register(TicketServiceSchemeSector)
class TicketServiceSchemeSectorAdmin(admin.ModelAdmin):
    actions = ('batch_set_cache',)
    fieldsets = (
        (
            None,
            {
                'fields': ('ticket_service_sector_id', 'ticket_service_sector_title',
                           'scheme', 'sector',),
                'classes': ('help_text',),
                'description': _('ticketserviceschemesector_sector_help_text'),
            }
        ),
    )
    list_display = ('ticket_service_sector_title', 'ticket_service_sector_id_short_description',
                    'if_sector_exists', 'scheme',)
    list_filter = (
        ('scheme', RelatedOnlyFieldDropdownFilter),
    )
    list_per_page = 20
    search_fields = ('ticket_service_sector_title',)

    @queryset_filter('Domain', 'scheme__ticket_service__domain__slug')
    def get_queryset(self, request):
        return super(TicketServiceSchemeSectorAdmin, self).get_queryset(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """В списке залов выводятся только залы в этом городе."""
        if db_field.name == 'scheme':
            city_filter = request.COOKIES.get('bezantrakta_admin_city', None)
            if city_filter is not None:
                kwargs['queryset'] = TicketServiceSchemeVenueBinder.objects.filter(
                    event_venue__city__slug=city_filter
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(TicketServiceSchemeSectorAdmin, self).save_model(request, obj, form, change)

        cache_factory(
            'ticket_service_scheme', obj.scheme.ticket_service_scheme_id, reset=True,
            ticket_service_id=obj.scheme.ticket_service_id
        )

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for obj in queryset:
            cache_factory(
                'ticket_service_scheme', obj.scheme.ticket_service_scheme_id, reset=True,
                ticket_service_id=obj.scheme.ticket_service_id
            )
    batch_set_cache.short_description = _('ticketserviceschemesector_admin_batch_set_cache')

    def if_sector_exists(self, obj):
        """Иконка обозначает, заполнена ли схема сектора."""
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        return _boolean_icon(True) if obj.sector != '' else _boolean_icon(False)
    if_sector_exists.short_description = _('ticketserviceschemesector_if_sector_exists')

    def ticket_service_sector_id_short_description(self, obj):
        """Короткая подпись для ID сектора при выводе списка в ``list_display``."""
        return obj.ticket_service_sector_id
    ticket_service_sector_id_short_description.short_description = _('ID')
