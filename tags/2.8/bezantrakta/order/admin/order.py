from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.urls import reverse

from project.decorators import queryset_filter
from project.shortcuts import build_absolute_url

from ..models import Order, OrderTicket


class OrderTicketInline(admin.TabularInline):
    model = OrderTicket
    extra = 0
    fields = ('id', 'price', 'bar_code', 'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', 'price_group_id',)
    readonly_fields = ('id', 'price', 'bar_code', 'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', 'price_group_id',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
    inlines = (OrderTicketInline,)
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

    def view_on_site(self, obj):
        url = reverse('order:confirmation', args=[obj.id])
        return build_absolute_url(obj.domain.slug, url)

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        return super(OrderAdmin, self).get_queryset(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if not settings.DEBUG:
            return False

    def order_uuid(self, obj):
        """Вывод нередактируемого уникального UUID заказа."""
        return obj.id
    order_uuid.short_description = _('order_admin_order_uuid')