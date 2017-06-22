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
    list_display = ('title', 'slug', 'mode', 'order', 'is_published',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'mode': admin.VERTICAL, }

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('img_width', 'img_height',)
        return self.readonly_fields
