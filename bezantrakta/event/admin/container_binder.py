from django.contrib import admin

from ..models import EventContainerBinder


class EventContainerBinderInline(admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('event_container', 'order', 'img', 'img_preview',)
    readonly_fields = ('img_preview',)
