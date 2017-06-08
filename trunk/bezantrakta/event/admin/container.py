from django.contrib import admin

from adminsortable2.admin import SortableInlineAdminMixin

from ..models import EventContainer, EventContainerBinder


class EventContainerBinderInline(SortableInlineAdminMixin, admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('order', 'event_container', 'img', 'img_preview', 'event_date',)
    readonly_fields = ('img_preview', 'event_date',)


@admin.register(EventContainer)
class EventContainerAdmin(admin.ModelAdmin):
    inlines = (EventContainerBinderInline,)
    list_display = ('title', 'slug', 'order', 'is_published',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    readonly_fields = ('img_width', 'img_height',)
