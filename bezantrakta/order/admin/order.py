import os

from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
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
    fields = readonly_fields = ('id', 'pdf_ticket', 'is_fixed', 'price', 'bar_code',
                                'sector_id', 'sector_title', 'row_id', 'seat_id', 'seat_title', )
    show_change_link = True
    template = 'admin/tabular_custom.html'

    def has_add_permission(self, request):
        """
        Добавлять в заказах произвольные билеты нельзя.
        Заказ состоит из билетов, заказанных покупателем на сайте.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """Удалять билеты в заказе может только суперадминистратор."""
        return True if request.user.is_superuser else False

    def pdf_ticket(self, obj):
        """Получение ссылки для скачивания PDF-билета."""
        # Название файла PDF-билета
        pdf_ticket = '{order_id}_{ticket_uuid}.pdf'.format(
            order_id=obj.ticket_service_order,
            ticket_uuid=obj.id
        )
        # Полный путь к файлу PDF-билета на сервере
        pdf_ticket_path = os.path.join(
            settings.BEZANTRAKTA_ETICKET_PATH,
            obj.domain.slug,
            pdf_ticket
        )

        pdf_file_exist = os.path.isfile(pdf_ticket_path)

        if pdf_file_exist:
            pdf_ticket_url = build_absolute_url(
                obj.domain.slug,
                reverse('order:download_pdf_ticket', args=[obj.domain.slug, obj.ticket_service_order, obj.id])
            )

            return mark_safe(
                '<a class="order_ticket_pdf_ticket" href="{pdf_ticket_url}">Скачать PDF-билет</a>'.format(
                    pdf_ticket_url=pdf_ticket_url
                )
            )
        else:
            return mark_safe('-')
    pdf_ticket.short_description = _('order_ticket_pdf_ticket')


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
class OrderAdmin(ImportExportMixin, admin.ModelAdmin):
    # Resource class for import
    if settings.DEBUG:
        resource_class = OrderImportResource

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
                'fields': ('name', 'email', 'phone',),
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
                    'name', 'email_link', 'phone_link',
                    'delivery', 'payment',
                    'status',
                    'ticket_service',)
    list_filter = (
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
        """Формирование ссылки "Смотреть на сайте"."""
        url = reverse('order:order_step_3', args=[obj.id])
        return build_absolute_url(obj.domain.slug, url)

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        """Фильтрация по выбранному сайту."""
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
            return ro_fields if request.user.is_superuser else ro_fields + ['status']

    def has_add_permission(self, request):
        """Создавать произвольные заказы вручную нельзя - они формируются пользователями сайта."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Созданные заказы может удалять только суперадминистратор."""
        return True if request.user.is_superuser else False

    def get_actions(self, request):
        """Отключение пакетного удаления по умолчанию для обычных администраторов."""
        actions = super(OrderAdmin, self).get_actions(request)
        if 'delete_selected' in actions and not request.user.is_superuser:
            del actions['delete_selected']
        return actions

    def order_uuid(self, obj):
        """Вывод нередактируемого уникального UUID заказа."""
        return obj.id
    order_uuid.short_description = _('order_admin_order_uuid')

    def email_link(self, obj):
        return mark_safe(
            '<a class="order_email_link" href="mailto:{email}?subject=Сообщение по заказу № {order}">{email}</a>'.format(email=obj.email, order=obj.ticket_service_order)
        )
    email_link.short_description = _('order_email_link')

    def phone_link(self, obj):
        return mark_safe(
            '<a class="order_phone_link" href="tel:{phone}">{phone}</a>'.format(phone=obj.phone)
        )
    phone_link.short_description = _('order_phone_link')
