from django.contrib import admin

# from adminsortable2.admin import SortableInlineAdminMixin

from project.decorators import queryset_filter
from ..models import EventContainer, EventContainerBinder


class EventContainerBinderInline(admin.TabularInline):  # SortableInlineAdminMixin
    model = EventContainerBinder
    extra = 0
    fields = ('order', 'event', 'event_datetime_localized', 'img', 'img_preview',)  # 'order_preview'
    readonly_fields = ('event', 'event_datetime_localized', 'img_preview',)
    template = 'admin/tabular_custom.html'

    @queryset_filter('Domain', 'event__domain__slug')
    def get_queryset(self, request):
        return super(EventContainerBinderInline, self).get_queryset(request)

    def has_add_permission(self, request):
        return False


@admin.register(EventContainer)
class EventContainerAdmin(admin.ModelAdmin):
    inlines = (EventContainerBinderInline,)
    list_display = ('title', 'slug', 'mode', 'is_published', 'order',)
    list_select_related = ()
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'mode': admin.VERTICAL, }

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('img_width', 'img_height',)
        return self.readonly_fields
