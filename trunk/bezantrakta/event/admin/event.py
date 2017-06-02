from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from ..models import Event
from bezantrakta.event_container.models import EventContainerBinder


class EventContainerBinderInline(admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('event_container', 'order', 'img', 'img_preview',)
    readonly_fields = ('img_preview',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'datetime', 'event_category', 'event_venue', 'is_published', 'is_on_index', 'domain',)
    radio_fields = {'min_age': admin.HORIZONTAL, }
    list_filter = (
        ('domain', RelatedDropdownFilter),
    )
    filter_horizontal = ('event_container',)
    inlines = (EventContainerBinderInline,)
