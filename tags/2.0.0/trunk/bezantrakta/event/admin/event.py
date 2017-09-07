from django.contrib import admin
from django.core.cache import cache
from django.utils.translation import ugettext as _

from project.decorators import queryset_filter
from ..cache import get_or_set_cache
from ..models import Event, EventCategory, EventContainerBinder, EventLinkBinder, EventGroupBinder


class EventGroupBinderInline(admin.TabularInline):
    model = EventGroupBinder
    extra = 0
    fk_name = 'group'
    fields = ('event', 'caption',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Для добавления в группу выводятся только привязанные к выбранному домену события.
        """
        if db_field.name == 'event':
            domain_filter = request.COOKIES.get('bezantrakta_admin_domain', None)
            kwargs['queryset'] = Event.objects.select_related(
                'event_category', 'event_venue', 'domain'
            ).filter(
                is_group=False,
                domain__slug=domain_filter
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class EventLinkBinderInline(admin.TabularInline):
    model = EventLinkBinder
    extra = 0
    fields = ('order', 'event_link', 'href', 'img_preview',)
    readonly_fields = ('img_preview',)


class EventContainerBinderInline(admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('order', 'event_container', 'img', 'img_preview',)
    readonly_fields = ('img_preview',)
    radio_fields = {'event_container': admin.VERTICAL, }


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    actions = ('publish_or_unpublish_items', 'batch_set_cache', 'delete_non_ticket_service_items')
    fieldsets = (
        (
            None,
            {
                'fields': ('title', 'slug', 'description', 'keywords', 'text',
                           'is_published', 'is_on_index', 'min_price', 'min_age',
                           'datetime', 'event_category', 'event_venue', 'domain', 'is_group',
                           'ticket_service', 'ticket_service_event', 'ticket_service_venue', 'ticket_service_prices',),
            }
        ),
    )
    filter_horizontal = ('event_container',)
    inlines = (EventGroupBinderInline, EventLinkBinderInline, EventContainerBinderInline,)
    list_display = ('title', 'is_published', 'is_on_index', 'datetime', 'event_category', 'event_venue',
                    'is_group', 'group_count', 'link_count', 'container_count',
                    'ticket_service', 'domain',)
    list_filter = (
        ('is_group', admin.BooleanFieldListFilter),
        ('ticket_service', admin.RelatedOnlyFieldListFilter),
    )
    list_select_related = ('event_category', 'event_venue', 'domain',)
    list_per_page = 20
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {
        'event_category': admin.VERTICAL,
        'min_age': admin.HORIZONTAL,
    }
    readonly_fields = ('ticket_service', 'ticket_service_event', 'ticket_service_venue', 'ticket_service_prices',)
    search_fields = ('title',)

    @queryset_filter('Domain', 'domain__slug')
    def get_queryset(self, request):
        return super(EventAdmin, self).get_queryset(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """В списке категорий событий выводятся только опубликованные категории."""
        if db_field.name == 'event_category':
            kwargs['queryset'] = EventCategory.objects.filter(is_published=True)
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        В событиях из сервисов продажи билетов нельзя изменить информацию,
        приходящую непосредственно из сервиса продажи билетов.
        """
        if obj is not None and obj.ticket_service is not None:
            return self.readonly_fields + ('datetime', 'is_group', 'event_venue', 'domain',)
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        """
        Импортируемые из сервисов продажи билетов события нельзя удалить,
        поскольку при каждом удалении они будут импортироваться снова.
        """
        if obj is not None and obj.ticket_service is not None:
            return False
        return super(EventAdmin, self).has_delete_permission(request, obj=obj)

    # def get_actions(self, request):
    #     """Отключение пакетного удаления по умолчанию."""
    #     actions = super(EventAdmin, self).get_actions(request)
    #     if 'delete_selected' in actions:
    #         del actions['delete_selected']
    #     return actions

    def delete_non_ticket_service_items(self, request, queryset):
        """
        Пакетное удаление только добавленных вручную групп/событий,
        т.е. не импортируемых из сервисов продажи билетов.
        """
        from django.contrib.admin.actions import delete_selected
        queryset = queryset.exclude(ticket_service__isnull=False)
        delete_selected(self, request, queryset)
    delete_non_ticket_service_items.short_description = _('event_admin_delete_non_ticket_service_items')

    def publish_or_unpublish_items(self, request, queryset):
        """Пакетная публикация или снятие с публикации групп/событий."""
        for item in queryset:
            if item.is_published:
                item.is_published = False
            else:
                item.is_published = True
            item.save(update_fields=['is_published'])
    publish_or_unpublish_items.short_description = _('event_admin_publish_or_unpublish_items')

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(EventAdmin, self).save_model(request, obj, form, change)

        if change and obj._meta.pk.name not in form.changed_data:
            get_or_set_cache(obj.id, reset=True)

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for item in queryset:
            get_or_set_cache(item.id, reset=True)
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
        """Число контейнеров для показа в разных позициях на сайте"""
        return obj.event_container.count()
    container_count.short_description = _('event_container_count')
