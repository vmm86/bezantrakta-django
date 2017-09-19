from django.contrib import admin

from project.decorators import domain_filter
# from ..forms import EventForm
from ..models import Event, EventCategory, EventContainerBinder, EventLinkBinder, EventGroupBinder


class EventGroupBinderInline(admin.TabularInline):
    model = EventGroupBinder
    extra = 0
    fk_name = 'group'
    fields = ('event', 'caption',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Для добавления в группу выводятся только привязанные к выбранному долмену события.
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
    # form = EventForm
    filter_horizontal = ('event_container',)
    inlines = (EventGroupBinderInline, EventLinkBinderInline, EventContainerBinderInline,)
    list_display = ('title', 'is_group', 'datetime', 'event_category', 'event_venue',
                    'is_published', 'is_on_index', 'group_count', 'link_count', 'container_count', 'domain',)
    list_filter = ('is_group',)
    list_select_related = ('event_category', 'event_venue', 'domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {
        'event_category': admin.VERTICAL,
        'min_age': admin.HORIZONTAL,
    }

    @domain_filter('domain__slug')
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event_category', 'event_venue', 'domain',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # В списке категорий событий выводятся только опубликованные категории.
        if db_field.name == 'event_category':
            kwargs['queryset'] = EventCategory.objects.filter(is_published=True)

        # В списке залов выводятся только залы выбранного для фильтрации города
        # domain_filter = request.COOKIES.get('bezantrakta_admin_domain', None)
        # if db_field.name == 'event_venue':
        #     if domain_filter:
        #         kwargs['queryset'] = EventVenue.objects.filter(domain__slug=domain_filter)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
