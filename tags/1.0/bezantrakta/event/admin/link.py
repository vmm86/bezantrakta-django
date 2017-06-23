from django.contrib import admin

from project.decorators import domain_filter
from ..models import EventLink, EventLinkBinder


class EventLinkBinderInline(admin.TabularInline):
    model = EventLinkBinder
    extra = 0
    fields = ('event', 'event_link', 'href', 'order',)
    readonly_fields = ('event', 'order',)

    @domain_filter('event__domain__slug')
    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return False


@admin.register(EventLink)
class EventLinkAdmin(admin.ModelAdmin):
    inlines = (EventLinkBinderInline,)
    list_display = ('title', 'slug', 'img_preview',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    readonly_fields = ('img_preview',)
