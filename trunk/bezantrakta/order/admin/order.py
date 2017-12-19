from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.urls import reverse

from rangefilter.filter import DateRangeFilter

from project.decorators import queryset_filter
from project.shortcuts import build_absolute_url

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import Order, OrderTicket


class OrderTicketInline(admin.TabularInline):
    model = OrderTicket
    extra = 0
    fields = ('id', 'price', 'bar_code', 'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', 'price_group_id',)
    readonly_fields = ('id', 'price', 'bar_code', 'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', 'price_group_id',)
    show_change_link = True
    template = 'admin/tabular_custom.html'

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
        ('datetime', DateRangeFilter),
        'status', 'delivery', 'payment',
        ('event', RelatedOnlyFieldDropdownFilter),
        ('ticket_service', admin.RelatedOnlyFieldListFilter),
    )
    list_per_page = 20
    radio_fields = {
        'status': admin.VERTICAL,
    }
    search_fields = ('name', 'phone', 'email',)

    def view_on_site(self, obj):
        url = reverse('order:confirmation', args=[obj.id])
        return build_absolute_url(obj.domain.slug, url)

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        return super(OrderAdmin, self).get_queryset(request)

    def get_readonly_fields(self, request, obj=None):
        """Полномочия пользователей при редактировании имеющихся или создании новых событий/групп."""
        # Суперадминистраторы при необходимости могут редактировать или создавать вручную события/группы,
        # например, если они по каким-то причинам НЕ исмпортировались из сервиса продажи билетов.
        ro_fields = [
            'order_uuid', 'ticket_service', 'ticket_service_order', 'event', 'ticket_service_event',
            'datetime',
            'delivery', 'payment', 'payment_id',
            'total', 'tickets_count',
            'domain',
        ]
        if obj is not None:
            return ro_fields if request.user.is_superuser else ro_fields + 'status'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if not settings.DEBUG:
            return False

    def order_uuid(self, obj):
        """Вывод нередактируемого уникального UUID заказа."""
        return obj.id
    order_uuid.short_description = _('order_admin_order_uuid')
