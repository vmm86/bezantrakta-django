from django.contrib import admin

from ..models import EventLink, EventLinkBinder


class EventLinkBinderInline(admin.TabularInline):
    model = EventLinkBinder
    extra = 0
    fields = ('event_link', 'href', 'order',)


@admin.register(EventLink)
class EventLinkAdmin(admin.ModelAdmin):
    inlines = (EventLinkBinderInline,)
    list_display = ('title', 'slug', 'img_preview',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    readonly_fields = ('img_preview',)
