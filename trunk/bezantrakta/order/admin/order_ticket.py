import os
from django.conf import settings
from django.contrib import admin
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from rangefilter.filter import DateRangeFilter

from project.decorators import queryset_filter
from project.shortcuts import build_absolute_url

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import OrderTicket


@admin.register(OrderTicket)
class OrderTicketAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Параметры заказа',
            {
                'fields': ('ticket_service_order', 'ticket_service', 'domain',),
            }
        ),
        (
            'Параметры билета',
            {
                'fields': ('id', 'bar_code',
                           'sector_id', 'sector_title',
                           'row_id',
                           'seat_id', 'seat_title',
                           'price', 'is_fixed', 'is_punched',),
            }
        ),
    )
    list_display = ('id', 'pdf_ticket', 'ticket_service_order',
                    'sector_title', 'row_id', 'seat_title', 'price', 'bar_code',
                    'ticket_service', 'domain',)
    list_filter = (
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
        """Фильтрация по выбранному сайту."""
        return super(OrderTicketAdmin, self).get_queryset(request)

    def has_add_permission(self, request):
        """Создавать произвольные билеты в заказах вручную нельзя - они добавляются в заказ пользователями сайта."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Существующие билеты в заказах может удалять только суперадминистратор."""
        return True if request.user.is_superuser else False

    def get_actions(self, request):
        """Отключение пакетного удаления по умолчанию для обычных администраторов."""
        actions = super(OrderTicketAdmin, self).get_actions(request)
        if 'delete_selected' in actions and not request.user.is_superuser:
            del actions['delete_selected']
        return actions

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
