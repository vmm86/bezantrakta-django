from django.conf import settings
from django.contrib import admin

from project.decorators import queryset_filter

from ..models import OrderTicket


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

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        return super(OrderTicketAdmin, self).get_queryset(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if not settings.DEBUG:
            return False
