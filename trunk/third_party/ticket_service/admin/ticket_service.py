from django.contrib import admin
from django.db.models import TextField
from django.utils.translation import ugettext as _

from jsoneditor.forms import JSONEditor

from project.cache import cache_factory

from ..models import TicketService, TicketServiceSchemeVenueBinder


class TicketServiceSchemeVenueBinderInline(admin.TabularInline):
    model = TicketServiceSchemeVenueBinder
    extra = 0
    fields = ('ticket_service_scheme_title', 'ticket_service_scheme_id', 'event_venue', 'ticket_service',)
    readonly_fields = ('ticket_service_scheme_title', 'ticket_service_scheme_id', 'ticket_service',)
    show_change_link = True
    template = 'admin/tabular_custom.html'

    def has_add_permission(self, request):
        return False


@admin.register(TicketService)
class TicketServiceAdmin(admin.ModelAdmin):
    actions = ('activate_or_deactivate_items', 'batch_set_cache',)
    inlines = (TicketServiceSchemeVenueBinderInline, )
    formfield_overrides = {
        TextField: {'widget': JSONEditor},
    }
    list_display = ('title', 'id', 'is_active', 'is_payment', 'ticket_service_schemes_count')
    list_per_page = 20

    fieldsets = (
        (
            None,
            {
                'fields': ('title', 'id', 'slug', 'is_active', 'domain', 'payment_service'),
            }
        ),
        (
            None,
            {
                'fields': ('settings',),
                'classes': ('json_settings',),
                'description': _('ticket_service_help_text'),
            }
        ),
    )

    prepopulated_fields = {
        'id': ('title',),
    }
    radio_fields = {'slug': admin.VERTICAL, }

    def get_queryset(self, request):
        return super(TicketServiceAdmin, self).get_queryset(request)

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(TicketServiceAdmin, self).save_model(request, obj, form, change)

        cache_factory('ticket_service', obj.id, reset=True)

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for obj in queryset:
            cache_factory('ticket_service', obj.id, reset=True)
    batch_set_cache.short_description = _('ticket_service_admin_batch_set_cache')

    def activate_or_deactivate_items(self, request, queryset):
        """Пакетная включение или отключение сервисов продажи билетов."""
        for obj in queryset:
            obj.is_active = False if obj.is_active else True
            obj.save(update_fields=['is_active'])

            cache_factory('ticket_service', obj.id, reset=True)

    activate_or_deactivate_items.short_description = _('event_admin_activate_or_deactivate_items')

    def ticket_service_schemes_count(self, obj):
        """Число связок со схемами залов из сервиса продажи билетов."""
        return obj.schemes.count()
    ticket_service_schemes_count.short_description = _('ticket_service_admin_ticket_service_schemes_count')

    def is_payment(self, obj):
        """Добавлен ли к сервису продажи билетов сервис онлайн-оплаты."""
        from django.contrib.admin.templatetags.admin_list import _boolean_icon
        return _boolean_icon(True) if obj.payment_service_id else _boolean_icon(False)
    is_payment.short_description = _('ticket_service_admin_is_payment_service_added')
