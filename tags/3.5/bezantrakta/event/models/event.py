import uuid

from ckeditor.fields import RichTextField

from django.db import models
from django.urls.base import reverse
from django.utils.translation import ugettext as _

from project.decorators import default_json_settings

from ..settings import EVENT_SETTINGS_DEFAULT


@default_json_settings(EVENT_SETTINGS_DEFAULT)
def default_json_settings_callable():
    pass


class EventManager(models.Manager):
    def get_queryset(self):
        return super(EventManager, self).get_queryset().select_related(
            'event_category', 'event_venue', 'domain'
        ).prefetch_related(
            'event_group', 'event_container', 'event_link'
        )


class Event(models.Model):
    """События, привязанные к какому-то билетному сервису или независимые (добавленные вручную).

    Attributes:
        objects (models.Manager): Менеджер модели.
        id (django.db.models.UUIDField): Уникальный идентификатор.
        title (django.db.models.CharField): Название.
        slug (django.db.models.SlugField): Псевдоним.
        description (django.db.models.TextField): Метатег ``description``.
        keywords (django.db.models.TextField): Метатег ``keywords``.
        text (ckeditor.fields.RichTextField): Текстовое описание события в HTML.
        is_published (django.db.models.BooleanField): Опубликовано или НЕ опубликовано.
        is_on_index (django.db.models.BooleanField): Показывать ли "на главной" в позициях ``small_vertical``.
        min_price (django.db.models.DecimalField): Минимальная цена на билет.
        min_age (django.db.models.PositiveSmallIntegerField): Ограничение по возрасту (по умолчанию - ``0``).

            Содержимое ``MIN_AGE_CHOICES`` (кортеж из кортежей "значение" / "подпись").
                * **AGE_00** (int): ``0``.
                * **AGE_06** (int): ``6``.
                * **AGE_12** (int): ``12``.
                * **AGE_16** (int): ``16``.
                * **AGE_18** (int): ``18``.

        datetime (django.db.models.DateTimeField): Дата/время события.
        event_category (django.db.models.ForeignKey): Привязка к категории события.
        event_venue (django.db.models.ForeignKey): Привязка к залу (месту проведения события).
        domain (django.db.models.ForeignKey): Привязка к сайту.
        is_group (django.db.models.BooleanField): Является ли запись в БД событием (``False``) или группой (``True``).
        event_group (django.db.models.ManyToManyField): Привязка событий к группе (если текущая запись в БД - группа).
        event_container (django.db.models.ManyToManyField): Привязка к категории событий.
        event_link (django.db.models.ManyToManyField): Привязка к внешним ссылкам с иконками.
        ticket_service (django.db.models.ForeignKey): Привязка к сервису продажи билетов.
        ticket_service_event (django.db.models.PositiveIntegerField): Идентификатор события в сервисе продажи билетов.
        ticket_service_scheme (django.db.models.PositiveIntegerField): Идентификатор схемы зала в сервисе продажи билетов.
        promoter (django.db.models.CharField): Организатор событий (промоутер).
        seller (django.db.models.CharField): Продавец билетов (агент).
        settings (django.db.models.TextField): Настройки в JSON.
    """
    objects = EventManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        help_text=_('event_title_help_text'),
        verbose_name=_('event_title'),
    )
    slug = models.SlugField(
        max_length=64,
        verbose_name=_('event_slug'),
    )
    description = models.TextField(
        max_length=200,
        help_text=_('event_description_help_text'),
        verbose_name=_('event_description'),
    )
    keywords = models.TextField(
        max_length=150,
        help_text=_('event_keywords_help_text'),
        verbose_name=_('event_keywords'),
    )
    text = RichTextField(
        verbose_name=_('event_text'),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('event_is_published'),
    )
    is_on_index = models.BooleanField(
        default=False,
        verbose_name=_('event_is_on_index'),
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('event_min_price'),
    )
    AGE_00 = 0
    AGE_06 = 6
    AGE_12 = 12
    AGE_16 = 16
    AGE_18 = 18
    MIN_AGE_CHOICES = (
        (AGE_00, '0+'),
        (AGE_06, '6+'),
        (AGE_12, '12+'),
        (AGE_16, '16+'),
        (AGE_18, '18+'),
    )
    min_age = models.PositiveSmallIntegerField(
        choices=MIN_AGE_CHOICES,
        default=AGE_00,
        blank=False,
        verbose_name=_('event_min_age'),
    )
    datetime = models.DateTimeField(
        verbose_name=_('event_datetime'),
    )
    event_category = models.ForeignKey(
        'event.EventCategory',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_column='event_category_id',
        verbose_name=_('event_event_category'),
    )
    event_venue = models.ForeignKey(
        'event.EventVenue',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_column='event_venue_id',
        verbose_name=_('event_event_venue'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('event_domain'),
    )
    is_group = models.BooleanField(
        default=False,
        verbose_name=_('event_is_group'),
    )
    event_group = models.ManyToManyField(
        'self',
        through='event.EventGroupBinder',
        through_fields=('group', 'event',),
        related_name='event_groups',
        symmetrical=False,
        blank=True,
        verbose_name=_('event_event_group'),
    )
    event_container = models.ManyToManyField(
        'event.EventContainer',
        through='event.EventContainerBinder',
        related_name='event_containers',
        blank=True,
        verbose_name=_('event_event_container'),
    )
    event_link = models.ManyToManyField(
        'event.EventLink',
        through='event.EventLinkBinder',
        related_name='event_links',
        blank=True,
        verbose_name=_('event_event_link'),
    )
    ticket_service = models.ForeignKey(
        'ticket_service.TicketService',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_column='ticket_service_id',
        verbose_name=_('event_ticket_service'),
    )
    ticket_service_event = models.PositiveIntegerField(
        blank=True,
        null=True,
        db_column='ticket_service_event_id',
        verbose_name=_('event_ticket_service_event'),
    )
    ticket_service_scheme = models.PositiveIntegerField(
        blank=True,
        null=True,
        db_column='ticket_service_scheme_id',
        verbose_name=_('event_ticket_service_scheme'),
    )
    promoter = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name=_('event_promoter'),
    )
    seller = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name=_('event_seller'),
    )
    settings = models.TextField(
        default=default_json_settings_callable,
        verbose_name=_('event_settings'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event'
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('domain', '-datetime', '-is_group', 'title',)
        unique_together = (
            ('domain', 'datetime', 'slug',),
        )

    def __str__(self):
        return '({datetime}) {title} - {event_or_group} - {ts_id} {domain}'.format(
            datetime=self.datetime.strftime('%d.%m.%Y'),
            title=self.title,
            event_or_group='группа' if self.is_group else 'событие',
            ts_id=self.ticket_service_event if self.ticket_service_event is not None else '',
            domain=self.domain.title,
        )

    def get_absolute_url(self):
        return reverse(
            'order:order_step_1',
            args=[
                str(self.datetime.year),
                str(self.datetime.month),
                str(self.datetime.day),
                str(self.datetime.hour),
                str(self.datetime.minute),
                self.slug
            ]
        )
