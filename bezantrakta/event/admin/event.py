from django.contrib import admin

from adminsortable2.admin import SortableInlineAdminMixin

from project.decorators import domain_filter
from ..models import Event, EventCategory, EventContainerBinder, EventLinkBinder, EventGroupBinder


class EventContainerBinderInline(admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('event_container', 'order', 'img', 'img_preview',)
    readonly_fields = ('order', 'img_preview',)
    radio_fields = {'event_container': admin.VERTICAL, }


class EventLinkBinderInline(SortableInlineAdminMixin, admin.TabularInline):
    model = EventLinkBinder
    extra = 0
    fields = ('order', 'event_link', 'href', 'img_preview',)
    readonly_fields = ('img_preview',)


class EventGroupBinderInline(admin.TabularInline):
    model = EventGroupBinder
    extra = 0
    fields = ('event_group',)
    readonly_fields = ('event_group',)

    def has_add_permission(self, request):
        return False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('event_container',)
    inlines = (EventContainerBinderInline, EventLinkBinderInline, EventGroupBinderInline,)
    list_display = ('title', 'datetime_localized', 'event_category', 'event_venue',
                    'is_published', 'is_on_index', 'container_count',
                    'link_count', 'domain',)
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
        return super().get_queryset(request)

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
