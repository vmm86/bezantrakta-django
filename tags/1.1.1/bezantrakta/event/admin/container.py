from django.contrib import admin

from adminsortable2.admin import SortableInlineAdminMixin

from project.decorators import domain_filter
from ..models import EventContainer, EventContainerBinder


class EventContainerBinderInline(SortableInlineAdminMixin, admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('order', 'event_container', 'order_preview', 'event_or_group', 'img', 'img_preview', 'event_datetime_localized',)
    readonly_fields = ('order_preview', 'event_or_group', 'img_preview', 'event_datetime_localized',)

    @domain_filter('event__domain__slug')
    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return False


@admin.register(EventContainer)
class EventContainerAdmin(admin.ModelAdmin):
    inlines = (EventContainerBinderInline,)
    list_display = ('title', 'slug', 'mode', 'is_published', 'order',)
    list_select_related = ()
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'mode': admin.VERTICAL, }

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('img_width', 'img_height',)
        return self.readonly_fields
