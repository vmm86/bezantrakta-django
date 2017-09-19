# import uuid

# from django.db import models
# from django.utils.translation import ugettext as _


# class EventGroup(models.Model):
#     """
#     Группы событий.
#     """
#     id = models.UUIDField(
#         primary_key=True,
#         default=uuid.uuid4,
#         editable=False,
#     )
#     title = models.CharField(
#         max_length=64,
#         help_text=_('eventgroup_title_help_text'),
#         verbose_name=_('eventgroup_title'),
#     )
#     slug = models.SlugField(
#         max_length=64,
#         verbose_name=_('eventgroup_slug'),
#     )
#     description = models.TextField(
#         max_length=200,
#         help_text=_('eventgroup_description_help_text'),
#         verbose_name=_('eventgroup_description'),
#     )
#     keywords = models.TextField(
#         max_length=150,
#         help_text=_('eventgroup_keywords_help_text'),
#         verbose_name=_('eventgroup_keywords'),
#     )
#     is_published = models.BooleanField(
#         default=False,
#         verbose_name=_('eventgroup_is_published'),
#     )
#     is_on_index = models.BooleanField(
#         default=False,
#         verbose_name=_('eventgroup_is_on_index'),
#     )
#     domain = models.ForeignKey(
#         'location.Domain',
#         on_delete=models.CASCADE,
#         db_column='domain_id',
#         verbose_name=_('eventgroup_domain'),
#     )

#     class Meta:
#         app_label = 'event'
#         db_table = 'bezantrakta_event_group'
#         verbose_name = _('eventgroup')
#         verbose_name_plural = _('eventgroups')
#         ordering = ('id', 'title',)
#         unique_together = (
#             ('domain', 'slug',),
#         )

#     def __str__(self):
#         return self.title

    # @property
    # def earliest_group_event(self):
    #     """
    #     Получение информации о самом раннем на данный момент событии в группе событий.
    #     """
    #     from django.db.models import F
    #     from .event import Event
    #     # from .container_binder import EventContainerBinder

    #     earliest_group_event = dict(Event.objects.select_related(
    #         'eventcontainerbinder',
    #         'eventgroupbinder',
    #     ).annotate(
    #         venue=F('event_venue__title'),
    #     ).values(
    #         'title',
    #         'slug',
    #         'datetime',
    #         'min_price',
    #         'min_age',
    #         'venue',
    #     ).filter(
    #         eventgroupbinder__event_group_id=self.id,
    #     ).order_by('datetime').first())

    #     return earliest_group_event

    # def event_slug(self):
    #     return self.earliest_group_event['slug']
    # event_slug.short_description = _('eventgroup_event_slug')

    # def datetime(self):
    #     return self.earliest_group_event['datetime']
    # datetime.short_description = _('eventgroup_datetime')

    # def min_price(self):
    #     return self.earliest_group_event['min_price']
    # datetime.short_description = _('eventgroup_min_price')

    # def min_age(self):
    #     return self.earliest_group_event['min_age']
    # datetime.short_description = _('eventgroup_min_age')

    # def venue(self):
    #     return self.earliest_group_event['venue']
    # datetime.short_description = _('eventgroup_venue')

    # def container_count(self):
    #     return self.event_container.count()
    # container_count.short_description = _('eventgroup_container_count')
