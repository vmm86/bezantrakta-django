from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.urls import reverse

from import_export import resources
from import_export.admin import ImportMixin, ExportMixin, ImportExportMixin

from rangefilter.filter import DateRangeFilter

from project.cache import cache_factory
from project.decorators import queryset_filter
from project.shortcuts import build_absolute_url, timezone_now

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..forms import EventForm
from ..models import Event, EventCategory, EventContainerBinder, EventLinkBinder, EventGroupBinder


class ListEventGroupBinderInline(admin.TabularInline):
    """
    Чтобы избежать множества избыточных SQL-запросов
    при выводе выпадающих списков в каждом связанном с группой событии,
    эти события выводятся в первой инлайн-форме
    без выбора событий в выпадающих списках,
    но с возможностью редактировать подпись события либо удалить события из группы.
    """
    model = EventGroupBinder
    extra = 0
    fk_name = 'group'
    fields = ('event', 'caption',)
    readonly_fields = ('event',)
    template = 'admin/tabular_custom.html'

    today = timezone_now()

    def get_queryset(self, request):
        """Вывод только актуальных на данный момент событий, ранее добавленных в группу."""
        return EventGroupBinder.objects.filter(
            event__datetime__gt=self.today
        )

    def has_add_permission(self, request):
        """При выводе имеющихся в группе событий возможность добавления отключена."""
        return False


class AddEventGroupBinderInline(admin.TabularInline):
    """
    Привязать новое событие к группе можно из второй инлайн-формы
    с возможностью добавления, но без возможности редактирования
    (без вывода уже добавленных событий).
    """
    model = EventGroupBinder
    extra = 0
    fk_name = 'group'
    fields = ('event', 'caption',)

    today = timezone_now()

    def has_change_permission(self, request, obj=None):
        """При добавлении новых событий в группу возможность редактирования отключена."""
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Для добавления в группу выводятся только актуальные события,
        привязанные к выбранному домену и ЕЩЁ НЕ добавленные в группу
        (одно событие нельзя добавить более чем в одну группу!).
        """
        if db_field.name == 'event':
            domain_filter = request.COOKIES.get('bezantrakta_admin_domain', None)
            kwargs['queryset'] = Event.objects.filter(
                is_group=False,
                event_groups__isnull=True,
                datetime__gt=self.today,
                domain__slug=domain_filter
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class EventLinkBinderInline(admin.TabularInline):
    model = EventLinkBinder
    extra = 0
    fields = ('order', 'event_link', 'href', 'img_preview',)
    readonly_fields = ('img_preview',)
    template = 'admin/tabular_custom.html'


class EventContainerBinderInline(admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('order', 'event_container', 'img', 'img_preview',)
    readonly_fields = ('img_preview',)
    radio_fields = {'event_container': admin.VERTICAL, }
    template = 'admin/tabular_custom.html'


class EventResource(resources.ModelResource):
    """Настройки импорта событий из старой версии сайта."""

    class Meta:
        model = Event
        fields = ('id', 'title', 'slug', 'description', 'keywords', 'text',
                  'is_published', 'is_on_index', 'min_price', 'min_age',
                  'datetime', 'event_category', 'event_venue', 'domain', 'is_group',
                  'ticket_service', 'ticket_service_event', 'ticket_service_scheme',
                  'promoter', 'seller', 'settings')
        skip_unchanged = True


# Опциональная возможность импорта старых событий в development-окружении
inheritance = (ImportMixin,) if settings.DEBUG else tuple()


@admin.register(Event)
class EventAdmin(*inheritance, admin.ModelAdmin):
    if settings.DEBUG:
        resource_class = EventResource

    actions = ('publish_or_unpublish_items', 'batch_set_cache', 'delete_non_ticket_service_items')
    fieldsets = (
        (
            None,
            {
                'fields': ('title', 'slug', 'description', 'keywords', 'text',
                           'is_published', 'is_on_index', 'min_price', 'min_age',
                           'datetime', 'event_category', 'event_venue', 'domain', 'is_group',

                           'ticket_service', 'ticket_service_event', 'ticket_service_scheme',
                           'promoter', 'seller',),
            }
        ),
        (
            None,
            {
                'fields': ('settings',),
                'classes': ('help_text',),
                'description': _('event_settings_help_text'),
            }
        ),
    )
    filter_horizontal = ('event_container',)
    form = EventForm
    group_inlines = (ListEventGroupBinderInline, AddEventGroupBinderInline, EventContainerBinderInline,)
    event_inlines = (EventLinkBinderInline, EventContainerBinderInline,)
    list_display = ('title', 'ticket_service_event_short_description', 'is_published', 'is_on_index', 'is_group',
                    'datetime', 'event_category', 'event_venue', 'ticket_service_scheme_short_description',
                    'group_count', 'link_count', 'container_count',
                    'ticket_service', 'domain',)
    list_filter = (
        ('is_published', admin.BooleanFieldListFilter),
        ('is_group', admin.BooleanFieldListFilter),
        ('datetime', DateRangeFilter),
        ('event_category', RelatedOnlyFieldDropdownFilter),
        ('event_venue', RelatedOnlyFieldDropdownFilter),
        ('ticket_service', RelatedOnlyFieldDropdownFilter),
    )
    list_select_related = ('event_category', 'event_venue', 'domain',)
    list_per_page = 50
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {
        'event_category': admin.VERTICAL,
        'min_age': admin.HORIZONTAL,
    }
    search_fields = ('title', 'ticket_service_scheme',)

    today = timezone_now()

    def get_view_on_site_url(self, obj=None):
        """Формирование ссылки "Смотреть на сайте"."""
        if obj is not None and obj.is_group is False:
            event_datetime_localized = obj.datetime.astimezone(obj.domain.city.timezone)

            url = reverse(
                'order:order_step_1',
                args=[
                    event_datetime_localized.strftime('%Y'),
                    event_datetime_localized.strftime('%m'),
                    event_datetime_localized.strftime('%d'),
                    event_datetime_localized.strftime('%H'),
                    event_datetime_localized.strftime('%M'),
                    obj.slug
                ]
            )

            return build_absolute_url(obj.domain.slug, url)
        else:
            return None

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        """Фильтрация по выбранному сайту."""
        return super(EventAdmin, self).get_queryset(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """В списке категорий событий выводятся только опубликованные категории."""
        if db_field.name == 'event_category':
            kwargs['queryset'] = EventCategory.objects.filter(is_published=True)
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """Полномочия пользователей при редактировании имеющихся или создании новых событий/групп."""
        # Суперадминистраторы при необходимости могут редактировать или создавать вручную события/группы,
        # например, если они по каким-то причинам НЕ исмпортировались из сервиса продажи билетов.
        ro_fields = []
        if request.user.is_superuser:
            if obj is not None and obj.ticket_service:
                ro_fields = ['ticket_service', 'ticket_service_event', 'ticket_service_scheme',
                             'is_group', 'domain', ]
                if obj.is_group:
                    ro_fields.append('promoter')
                    ro_fields.append('seller')
            # print('ro_fields: ', ro_fields)
            return ro_fields
        # Обычные администраторы в любом случае НЕ могут изменить информацию, относящуюся к сервису продажи билетов.
        else:
            ro_fields = ['ticket_service', 'ticket_service_event', 'ticket_service_scheme',
                         'is_group', 'event_venue', 'domain', ]
            if obj is not None and obj.ticket_service:
                if obj.is_group:
                    ro_fields.append('promoter')
                    ro_fields.append('seller')
                else:
                    ro_fields.append('datetime')
            # print('ro_fields: ', ro_fields)
            return ro_fields

    def get_form(self, request, obj=None, **kwargs):
        """Инлайн-формы показываются в зависимости от того, событие это или группа.

        Добавление событий в группе работает только для группы.
        Добавление ссылок работает только для событий.
        """
        if obj is not None:
            self.inlines = self.group_inlines if obj.is_group else self.event_inlines
        return super(EventAdmin, self).get_form(request, obj, **kwargs)

    def has_delete_permission(self, request, obj=None):
        """Импортируемые из сервисов продажи билетов события нельзя удалить,
        поскольку при каждом удалении они будут импортироваться снова.
        """
        if obj is not None and obj.ticket_service is not None and not request.user.is_superuser:
            return False
        return super(EventAdmin, self).has_delete_permission(request, obj=obj)

    def get_actions(self, request):
        """Отключение пакетного удаления по умолчанию для обычных администраторов."""
        actions = super(EventAdmin, self).get_actions(request)
        if 'delete_selected' in actions and not request.user.is_superuser:
            del actions['delete_selected']
        return actions

    def delete_non_ticket_service_items(self, request, queryset):
        """Пакетное удаление только добавленных вручную групп/событий, НЕ импортируемых из сервисов продажи билетов."""
        from django.contrib.admin.actions import delete_selected
        queryset = queryset.exclude(ticket_service__isnull=False)
        delete_selected(self, request, queryset)
    delete_non_ticket_service_items.short_description = _('event_admin_delete_non_ticket_service_items')

    def publish_or_unpublish_items(self, request, queryset):
        """Пакетная публикация или снятие с публикации групп/событий с последующим пересозданием кэша."""
        for obj in queryset:
            obj.is_published = False if obj.is_published else True
            obj.save(update_fields=['is_published'])

            # Обновить кэш группы (и всех его актуальных событий) или события (и его группы, если она имеется)
            self.update_event_or_group_cache(obj)

    publish_or_unpublish_items.short_description = _('event_admin_publish_or_unpublish_items')

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(EventAdmin, self).save_model(request, obj, form, change)

        # Обновить кэш группы (и всех его актуальных событий) или события (и его группы, если она имеется)
        self.update_event_or_group_cache(obj)

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for obj in queryset:
            # Обновить кэш группы (и всех его актуальных событий) или события (и его группы, если она имеется)
            self.update_event_or_group_cache(obj)

    batch_set_cache.short_description = _('event_admin_batch_set_cache')

    def group_count(self, obj):
        """Число событий в группе"""
        return obj.event_group.count()
    group_count.short_description = _('event_group_count')

    def link_count(self, obj):
        """Число ссылок"""
        return obj.event_link.count()
    link_count.short_description = _('event_link_count')

    def container_count(self, obj):
        """Число афиш в контейнерах для показа в разных позициях на сайте.

        Считаются все афиши, кроме маленьких вертикальных в любой позиции и маленькие верикальные в позиции больше 0.
        """
        return obj.event_container.count()
    container_count.short_description = _('event_container_count')

    def ticket_service_event_short_description(self, obj):
        """Короткая подпись для ID события или группы при выводе списка в ``list_display``."""
        return obj.ticket_service_event
    ticket_service_event_short_description.short_description = _('ID')

    def ticket_service_scheme_short_description(self, obj):
        """Короткая подпись для ID схемы зала при выводе списка в ``list_display``."""
        return obj.ticket_service_scheme
    ticket_service_scheme_short_description.short_description = _('Схема')

    def update_event_or_group_cache(self, obj):
        """Обновить кэш группы (и всех его актуальных событий) или события (и его группы, если она имеется)."""
        # Если обновляется кэш группы - принудительно обновить кэш всех её актуальных событий
        if obj.is_group:
            group = cache_factory('group', obj.id, reset=True)

            if group['events_in_group']:
                for event_uuid in group['events_in_group']:
                    cache_factory('event', event_uuid, reset=True)
        # Если обновляется кэш события - принудительно обновить кэш его группы, если событие в неё входит
        elif obj.event_groups:
            event = cache_factory('event', obj.id, reset=True)

            if event['group_uuid']:
                cache_factory('group', event['group_uuid'], reset=True)
