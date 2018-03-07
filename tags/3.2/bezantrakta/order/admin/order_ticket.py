from django.contrib import admin

from rangefilter.filter import DateRangeFilter

from project.decorators import queryset_filter

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import OrderTicket


@admin.register(OrderTicket)
class OrderTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_service_order',
                    'sector_title', 'row_id', 'seat_title', 'price', 'bar_code',
                    'ticket_service', 'domain',)
    list_filter = (
        # ('order__datetime', DateRangeFilter),
        'order__status', 'order__delivery', 'order__payment',
        ('order__event', RelatedOnlyFieldDropdownFilter),
        ('order__event__datetime', DateRangeFilter),
        ('ticket_service', admin.RelatedOnlyFieldListFilter),
    )
    list_per_page = 20
    readonly_fields = ('id', 'order', 'ticket_service', 'ticket_service_order',
                       'is_fixed', 'is_punched', 'bar_code',
                       'ticket_id', 'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', 'price',
                       'domain',)
    search_fields = ('ticket_service_order', 'order__name', 'order__phone', 'order__email',)

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        return super(OrderTicketAdmin, self).get_queryset(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True if request.user.is_superuser else False
