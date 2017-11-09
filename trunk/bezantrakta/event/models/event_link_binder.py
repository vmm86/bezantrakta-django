import uuid

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class EventLinkBinderManager(models.Manager):
    def get_queryset(self):
        return super(EventLinkBinderManager, self).get_queryset().select_related('event', 'event_link')


class EventLinkBinder(models.Model):
    """Связующая таблица событий и ссылок.

    Attributes:
        objects (EventLinkBinderManager): Менеджер модели.
        id (UUIDField): Уникальный идентификатор.
        event (ForeignKey): Привязка к событию.
        event_link (ForeignKey): Привязка к внешней ссылке на стороннего продавца билетов.
        href (URLField): URL внешней ссылки на конкретную стороннюю страницу продажи билетов.
        order (PositiveSmallIntegerField): Порядок иконок внешних ссылок на странице события.
    """
    objects = EventLinkBinderManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        db_column='event_id',
        verbose_name=_('eventlinkbunder_event'),
    )
    event_link = models.ForeignKey(
        'event.EventLink',
        on_delete=models.CASCADE,
        db_column='event_link_id',
        verbose_name=_('eventlinkbunder_event_link'),
    )
    href = models.URLField(
        blank=True,
        verbose_name=_('eventlinkbunder_href'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('eventlinkbunder_order'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_link_binder'
        verbose_name = _('eventlinkbunder')
        verbose_name_plural = _('eventlinkbunders')
        ordering = ('order', 'event', 'event_link',)
        unique_together = (
            ('event', 'event_link',),
        )

    def __str__(self):
        return '{event} 🔗 {link}'.format(
            event=self.event,
            link=self.event_link
        )

    def order_preview(self):
        return self.order
    order_preview.short_description = _('eventlinkbunder_order')

    def img_preview(self):
        return mark_safe('<img class="img_preview_linkbinder" src="{url}">'.format(url=self.event_link.img.url))
    img_preview.short_description = _('eventlinkbunder_img_preview')

    def event_datetime_localized(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        # Дата и время события в часовом поясе его города
        current_timezone = self.event.domain.city.timezone
        event_datetime_localized = self.event.datetime.astimezone(current_timezone)
        return mark_safe(
            '{date} {time}'.format(
                date=naturalday(event_datetime_localized),
                time=event_datetime_localized.strftime('%H:%M'),
            )
        )
    event_datetime_localized.short_description = _('eventcontainerbinder_event_datetime')
