from django.contrib import admin

from adminsortable2.admin import SortableInlineAdminMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from ..models import Event, EventContainerBinder, EventLinkBinder


class EventContainerBinderInline(admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('event_container', 'order', 'img', 'img_preview',)
    readonly_fields = ('img_preview',)


class EventLinkBinderInline(SortableInlineAdminMixin, admin.TabularInline):
    model = EventLinkBinder
    extra = 0
    fields = ('order', 'event_link', 'href', 'img_preview',)
    readonly_fields = ('img_preview',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('event_container',)
    inlines = (EventContainerBinderInline, EventLinkBinderInline,)
    list_display = ('title', 'date', 'time', 'event_category', 'event_venue',
                    'is_published', 'is_on_index', 'container_count',
                    'link_count', 'domain',)
    list_filter = (
        ('domain', RelatedDropdownFilter),
    )
    list_select_related = ('event_category', 'event_venue', 'domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'min_age': admin.HORIZONTAL, }
