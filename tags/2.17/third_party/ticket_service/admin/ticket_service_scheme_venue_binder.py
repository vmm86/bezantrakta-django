from django.contrib import admin
from django.utils.translation import ugettext as _

from project.cache import cache_factory
from project.decorators import queryset_filter

from bezantrakta.event.models import EventVenue
from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import TicketServiceSchemeVenueBinder, TicketServiceSchemeSector


class TicketServiceSchemeSectorInline(admin.TabularInline):
    model = TicketServiceSchemeSector
    extra = 0
    fields = ('ticket_service_sector_title', 'ticket_service_sector_id', 'sector',)
    template = 'admin/tabular_custom.html'


@admin.register(TicketServiceSchemeVenueBinder)
class TicketServiceSchemeVenueBinderAdmin(admin.ModelAdmin):
    actions = ('batch_set_cache',)
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
    list_display = ('ticket_service_scheme_title', 'ticket_service_scheme_id_short_description',
                    'if_scheme_exists', 'if_sectors_exist', 'ticket_service',)
    list_filter = (
        ('event_venue', RelatedOnlyFieldDropdownFilter),
        ('ticket_service', admin.RelatedOnlyFieldListFilter),
    )
    list_per_page = 20
    readonly_fields = ('ticket_service', 'ticket_service_scheme_id',)
    search_fields = ('ticket_service_scheme_title',)

    @queryset_filter('Domain', 'ticket_service__domain__slug')
    def get_queryset(self, request):
        return super(TicketServiceSchemeVenueBinderAdmin, self).get_queryset(request)

    def has_add_permission(self, request):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """В списке залов выводятся только залы в этом городе."""
        if db_field.name == 'event_venue':
            city_filter = request.COOKIES.get('bezantrakta_admin_city', None)
            if city_filter is not None:
                kwargs['queryset'] = EventVenue.objects.filter(
                    city__slug=city_filter
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(TicketServiceSchemeVenueBinderAdmin, self).save_model(request, obj, form, change)

        if change and obj._meta.pk.name not in form.changed_data:
            cache_factory(
                'ticket_service_scheme', obj.ticket_service_scheme_id, reset=True,
                ticket_service_id=obj.ticket_service_id
            )

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for item in queryset:
            cache_factory(
                'ticket_service_scheme', item.ticket_service_scheme_id, reset=True,
                ticket_service_id=item.ticket_service_id
            )
    batch_set_cache.short_description = _('ticketservicevenuebinder_admin_batch_set_cache')

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

    def ticket_service_scheme_id_short_description(self, obj):
        """Короткая подпись для ID схемы зала при выводе списка в ``list_display``."""
        return obj.ticket_service_scheme_id
    ticket_service_scheme_id_short_description.short_description = _('ID')
