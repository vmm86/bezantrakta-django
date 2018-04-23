import os

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.urls import reverse

from django_object_actions import DjangoObjectActions

from import_export import resources
from import_export.admin import ImportMixin, ExportMixin, ImportExportMixin
from import_export.formats import base_formats

from rangefilter.filter import DateRangeFilter

from project.decorators import queryset_filter
from project.shortcuts import build_absolute_url

from api.object_actions.order import email_resend, cancel, refund

from bezantrakta.event.models import Event
from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from bezantrakta.order.order_basket import OrderBasket
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
    """Настройки импорта заказов из старой версии сайта."""

    class Meta:
        model = Order
        fields = ('id', 'ticket_service', 'ticket_service_order',
                  'event', 'ticket_service_event',
                  'datetime', 'name', 'email', 'phone', 'address',
                  'delivery', 'payment', 'payment_id', 'status',
                  'tickets_count', 'total', 'overall', 'domain')
        skip_unchanged = True


class OrderExportResource(resources.ModelResource):
    """Настройки экспорта заказов."""
    fk_model = Event

    class Meta:
        model = Order
        fields = export_order = (
            'event__datetime', 'event__title',
            'ticket_service_order', 'datetime',
            'tickets_count', 'total', 'overall',
            'name', 'email', 'phone',
            'delivery', 'payment', 'status',
        )

    def dehydrate_datetime(self, order):
        """Человекопонятная дата/время заказа."""
        return '{:%d.%m.%Y %H:%M}'.format(order.datetime)

    def dehydrate_event__datetime(self, order):
        """Человекопонятная дата/время события."""
        return '{:%d.%m.%Y %H:%M}'.format(order.event.datetime)

    def dehydrate_delivery(self, order):
        """Русскоязычное название способа получения билетов."""
        return OrderBasket.ORDER_DELIVERY_CAPTION[order.delivery]

    def dehydrate_payment(self, order):
        """Русскоязычное название способа оплаты."""
        return OrderBasket.ORDER_PAYMENT_CAPTION[order.payment]

    def dehydrate_status(self, order):
        """Русскоязычное название статуса заказа."""
        return OrderBasket.ORDER_STATUS_CAPTION[order.status]['description']

    def get_export_headers(self):
        """Получение русскоязычных заголовков для экспортируемых полей.

        Названия связей по внешнему ключу берутся из заданной модели ``fk_model``.
        """
        headers = []
        for field in self._meta.fields:
            try:
                field_title = self._meta.model._meta.get_field(field).verbose_name
            except FieldDoesNotExist:
                try:
                    field = field.split('__')[1]
                    field_title = self.fk_model._meta.get_field(field).verbose_name
                except FieldDoesNotExist:
                    field_title = field
            headers.append(field_title)

        return headers


# Опциональная возможность импорта старых заказов в development-окружении (экспорт в любом случае возможен)
inheritance = [ImportExportMixin, ] if settings.DEBUG else [ExportMixin, ]
inheritance.append(DjangoObjectActions)


@admin.register(Order)
class OrderAdmin(*inheritance, admin.ModelAdmin):
    if settings.DEBUG:
        resource_class = OrderImportResource

    def get_export_resource_class(self):
        return OrderExportResource

    # Рекомендуется экспортировать данные в формате XLS, ODS или CSV.
    # С другими форматами могут возникать ошибки при экспорте.
    formats = (
        base_formats.CSV,
        base_formats.XLS,
        # base_formats.XLSX,
        # base_formats.TSV,
        base_formats.ODS,
        # base_formats.JSON,
        # base_formats.YAML,
        # base_formats.HTML,
    )

    def get_export_queryset(self, request):
        """Упорядочить экспортируемые заказы по дате/времени события по убыванию."""
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)

        change_list = self.get_changelist(request)
        cl = change_list(
            request, self.model, list_display,
            list_display_links, self.list_filter,
            self.date_hierarchy, self.search_fields,
            self.list_select_related, self.list_per_page,
            self.list_max_show_all, self.list_editable,
            self
        )

        return cl.queryset.order_by('-event__datetime')

    # date_hierarchy = 'event__datetime'

    change_actions = ('email_resend_action', 'cancel_action', 'refund_action',)
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

    def get_change_actions(self, request, object_id, form_url):
        """Условное получение действий при открытии заказа."""
        actions = []

        obj = self.model.objects.get(pk=object_id)

        if obj.status == 'approved':
            if obj.payment == 'cash':
                actions.append('cancel_action')
            actions.append('refund_action')
            actions.append('email_resend_action')

        actions = tuple(actions)

        return actions

    def cancel_action(self, request, obj):
        """Отмена заказа при оффлайн-оплате."""
        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(request)
        changelist_url = reverse('admin:order_order_changelist')

        redirect_url = add_preserved_filters(
            {'preserved_filters': preserved_filters, 'opts': opts},
            changelist_url
        )

        order_uuid = obj.id

        response = cancel(order_uuid)
        level = messages.INFO if response['success'] else messages.ERROR
        self.message_user(request, response['message'], level=level)

        # Возврат к списку заказов
        return redirect(redirect_url)
    cancel_action.label = _('order_admin_cancel_action')

    def refund_action(self, request, obj):
        """Возврат стоимости заказа."""
        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(request)
        changelist_url = reverse('admin:order_order_changelist')

        redirect_url = add_preserved_filters(
            {'preserved_filters': preserved_filters, 'opts': opts},
            changelist_url
        )

        # Если возврат выполнен
        if request.method == 'POST':
            order_uuid = obj.id
            amount = request.POST.get('amount', obj.total)
            reason = request.POST.get('reason', '')
            if reason == 'other':
                reason = request.POST.get('reason_other', '')

            response = refund(order_uuid, amount, reason)
            level = messages.INFO if response['success'] else messages.ERROR
            self.message_user(request, response['message'], level=level)

            # Возврат к списку заказов
            return redirect(redirect_url)

        context = {
            'opts': opts,
            'amount': obj.total,
            'order_uuid': obj.id,
            'order_id': obj.ticket_service_order,
        }

        return render(
            request,
            'admin/object_actions/refund.html',
            context=context
        )
    refund_action.label = _('order_admin_refund_action')

    def email_resend_action(self, request, obj):
        """Повторная отправка email-сообщения о заказе покупателю."""
        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(request)
        changelist_url = reverse('admin:order_order_changelist')

        redirect_url = add_preserved_filters(
            {'preserved_filters': preserved_filters, 'opts': opts},
            changelist_url
        )

        order_uuid = obj.id

        response = email_resend(order_uuid)
        level = messages.INFO if response['success'] else messages.ERROR
        self.message_user(request, response['message'], level=level)

        # Возврат к списку заказов
        return redirect(redirect_url)
    email_resend_action.label = _('order_admin_email_resend_action')

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
