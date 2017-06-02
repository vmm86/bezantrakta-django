from django.contrib import admin

from adminsortable2.admin import SortableInlineAdminMixin

from ..models import EventContainer, EventContainerBinder


class EventContainerBinderInline(SortableInlineAdminMixin, admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('order', 'event_container', 'img', 'img_preview',)
    readonly_fields = ('img_preview',)


@admin.register(EventContainer)
class EventContainerAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'order', 'is_published',)
    readonly_fields = ('img_width', 'img_height',)
    inlines = (EventContainerBinderInline,)
