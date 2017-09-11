from django.contrib import admin
from django.core.cache import cache
from django.db.models import TextField
from django.utils.translation import ugettext as _

from jsoneditor.forms import JSONEditor

from ..cache import get_or_set_cache
from ..models import TicketService, TicketServiceSchemeVenueBinder


class TicketServiceSchemeVenueBinderInline(admin.TabularInline):
    model = TicketServiceSchemeVenueBinder
    extra = 0
    fields = ('ticket_service', 'ticket_service_scheme_id', 'ticket_service_scheme_title', 'event_venue',)
    readonly_fields = ('ticket_service', 'ticket_service_scheme_id', 'ticket_service_scheme_title',)

    def has_add_permission(self, request):
        return False


@admin.register(TicketService)
class TicketServiceAdmin(admin.ModelAdmin):
    actions = ('activate_or_deactivate_items', 'batch_set_cache',)
    inlines = (TicketServiceSchemeVenueBinderInline, )
    formfield_overrides = {
        TextField: {'widget': JSONEditor},
    }
    prepopulated_fields = {
        'id': ('title',),
    }
    list_display = ('title', 'id', 'is_active', 'is_payment', 'ticket_service_schemes_count')
    list_per_page = 10

    fieldsets = (
        (
            None,
            {
                'fields': ('id', 'title', 'slug', 'is_active', 'domain', 'payment_service'),
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

    def get_queryset(self, request):
        return super(TicketServiceAdmin, self).get_queryset(request)

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(TicketServiceAdmin, self).save_model(request, obj, form, change)

        if change and obj._meta.pk.name not in form.changed_data:
            get_or_set_cache(obj.id, reset=True)

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for item in queryset:
            get_or_set_cache(item.id, reset=True)
    batch_set_cache.short_description = _('ticket_service_admin_batch_set_cache')

    def activate_or_deactivate_items(self, request, queryset):
        """Пакетная включение или отключение сервисов продажи билетов."""
        for item in queryset:
            if item.is_active:
                item.is_active = False
            else:
                item.is_active = True
            item.save(update_fields=['is_active'])
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
