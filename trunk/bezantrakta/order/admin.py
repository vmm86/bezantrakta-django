from django.conf import settings
from django.contrib import admin
# from django.core.cache import cache
from django.utils.translation import ugettext as _

# from .cache import get_or_set_cache
from .models import Order, OrderTicket


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Параметры заказа',
            {
                'fields': ('domain', 'ticket_service', 'order_uuid', 'ticket_service_order',
                           'event', 'ticket_service_event', 'datetime',
                           'delivery', 'payment', 'payment_id', 'status',),
            }
        ),
        (
            'Билеты',
            {
                'fields': ('total', 'tickets_count',),
            }
        ),
        (
            'Реквизиты покупателя',
            {
                'fields': ('name', 'phone', 'email',),
            }
        ),
    )
    list_display = ('ticket_service_order', 'datetime',
                    'total', 'tickets_count',
                    'name', 'email', 'phone',
                    'delivery', 'payment',
                    'status',
                    'ticket_service',)
    list_filter = (
        'status', 'delivery', 'payment',
        ('ticket_service', admin.RelatedOnlyFieldListFilter),
    )
    list_per_page = 20
    readonly_fields = ('order_uuid', 'ticket_service', 'ticket_service_order', 'event', 'ticket_service_event',
                       'datetime', 'name', 'phone', 'email',
                       'delivery', 'payment', 'payment_id',
                       'status', 'total', 'tickets_count',
                       'domain',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if not settings.DEBUG:
            return False

    # def save_model(self, request, obj, form, change):
    #     """Пересоздать кэш:
    #     * при сохранении созданной ранее записи,
    #     * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
    #     """
    #     if change and obj._meta.pk.name not in form.changed_data:
    #         cache_key = 'order.{order_uuid}'.format(order_uuid=obj.id)
    #         cache.delete(cache_key)
    #         get_or_set_cache(obj.id)

    #     super(OrderAdmin, self).save_model(request, obj, form, change)

    def order_uuid(self, obj):
        """Вывод нередактируемого уникального UUID заказа."""
        return obj.id
    order_uuid.short_description = _('order_admin_order_uuid')


@admin.register(OrderTicket)
class OrderTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_service_order',
                    'sector_title', 'row_id', 'seat_title', 'price', 'bar_code',
                    'ticket_service', 'domain',)
    list_per_page = 20
    readonly_fields = ('id', 'order', 'ticket_service', 'ticket_service_order',
                       'is_punched', 'bar_code',
                       'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', 'price_group_id', 'price',
                       'domain',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if not settings.DEBUG:
            return False
