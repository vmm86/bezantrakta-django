from django.contrib import admin
from django.utils.translation import ugettext as _
from django.urls import reverse

from import_export import resources
from import_export.admin import ImportMixin, ExportMixin, ImportExportMixin

from rangefilter.filter import DateRangeFilter

from project.decorators import queryset_filter
from project.shortcuts import build_absolute_url

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import Order, OrderTicket


class OrderTicketInline(admin.TabularInline):
    model = OrderTicket
    extra = 0
    fields = ('id', 'ticket_id', 'is_fixed', 'price', 'bar_code',
              'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', )
    readonly_fields = ('id', 'ticket_id', 'is_fixed', 'price', 'bar_code',
                       'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', )
    show_change_link = True
    template = 'admin/tabular_custom.html'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True if request.user.is_superuser else False


class OrderImportResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('id', 'ticket_service', 'ticket_service_order', 'event', 'ticket_service_event',
                  'datetime', 'name', 'email', 'phone', 'address',
                  'delivery', 'payment', 'payment_id', 'status',
                  'tickets_count', 'total', 'overall', 'domain')
        skip_unchanged = True


class OrderExportResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('id', 'ticket_service_order',
                  'datetime', 'name', 'email', 'phone',
                  'delivery', 'payment', 'status',
                  'tickets_count', 'total', 'overall')


@admin.register(Order)
class OrderAdmin(ExportMixin, admin.ModelAdmin):
    # Resource class for import
    # resource_class = OrderImportResource

    # Resource class for export
    def get_export_resource_class(self):
        return OrderExportResource

    # date_hierarchy = 'event__datetime'

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
            'Реквизиты покупателя',
            {
                'fields': ('name', 'phone', 'email',),
            }
        ),
        (
            'Билеты',
            {
                'fields': ('tickets_count', 'total', 'overall',),
            }
        ),
    )
    inlines = (OrderTicketInline,)
    list_display = ('ticket_service_order', 'datetime',
                    'total', 'overall', 'tickets_count',
                    'name', 'email', 'phone',
                    'delivery', 'payment',
                    'status',
                    'ticket_service',)
    list_filter = (
        # ('datetime', DateRangeFilter),
        'status', 'delivery', 'payment',
        ('event', RelatedOnlyFieldDropdownFilter),
        ('event__datetime', DateRangeFilter),
        ('ticket_service', RelatedOnlyFieldDropdownFilter),
    )
    list_per_page = 20
    radio_fields = {
        'status': admin.VERTICAL,
    }
    search_fields = ('ticket_service_order', 'name', 'phone', 'email',)

    def view_on_site(self, obj):
        url = reverse('order:order_step_3', args=[obj.id])
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
            'total', 'overall', 'tickets_count',
            'domain',
        ]
        if obj is not None:
            return ro_fields if request.user.is_superuser else ro_fields + 'status'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True if request.user.is_superuser else False

    def order_uuid(self, obj):
        """Вывод нередактируемого уникального UUID заказа."""
        return obj.id
    order_uuid.short_description = _('order_admin_order_uuid')
