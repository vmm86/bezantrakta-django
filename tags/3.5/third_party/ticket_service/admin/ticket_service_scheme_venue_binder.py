from django.contrib import admin
from django.utils.translation import ugettext as _

from project.cache import cache_factory
from project.decorators import queryset_filter

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
                'fields': ('ticket_service_scheme_title', 'ticket_service', 'ticket_service_scheme_id',
                           'event_venue',),
            }
        ),
        (
            None,
            {
                'fields': ('scheme',),
                'classes': ('help_text',),
                'description': _('ticketserviceschemevenuebinder_scheme_help_text'),
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
    search_fields = ('ticket_service_scheme_title', 'scheme',)

    @queryset_filter('Domain', 'ticket_service__domain__slug')
    def get_queryset(self, request):
        return super(TicketServiceSchemeVenueBinderAdmin, self).get_queryset(request)

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        # Не сохранять экземпляр модели в методе по умолчанию,
        # чтобы сначала сохранить все секторы, затем схему,
        # и только после этого пересоздать кэш схемы зала
        if not obj.pk:
            super(TicketServiceSchemeVenueBinderAdmin, self).save_model(request, obj, form, change)
        else:
            pass

    def save_formset(self, request, form, formset, change):
        # Сохранить сначала схемы всех секторов в inline-формах
        formset.save()
        # Затем сохранить саму схему зала (обычную или посекторную)
        form.instance.save()

        # Пересоздать кэш схемы зала (с секторами или без)
        cache_factory(
            'ticket_service_scheme', form.instance.ticket_service_scheme_id, reset=True,
            ticket_service_id=form.instance.ticket_service_id
        )

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for obj in queryset:
            cache_factory(
                'ticket_service_scheme', obj.ticket_service_scheme_id, reset=True,
                ticket_service_id=obj.ticket_service_id
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
