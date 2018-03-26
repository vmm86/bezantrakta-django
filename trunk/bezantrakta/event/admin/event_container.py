from django.contrib import admin

from project.decorators import queryset_filter
from project.shortcuts import timezone_now
from ..models import EventContainer, EventContainerBinder


class EventContainerBinderInline(admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('order', 'event', 'event_datetime_localized', 'img', 'img_preview',)
    readonly_fields = ('event', 'event_datetime_localized', 'img_preview',)
    template = 'admin/tabular_custom.html'

    today = timezone_now()

    @queryset_filter('Domain', 'event__domain__slug')
    def get_queryset(self, request):
        """Фильтрация по выбранному сайту."""
        return EventContainerBinder.objects.filter(
            event__datetime__gt=self.today
        )

    def has_add_permission(self, request):
        """Афиши, добавленные в конкретных событиях, здесь выводятся без возможности добавления."""
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
        """Ширина и высота афиш в контейнерах для обычных администарторов доступны только для чтения."""
        if not request.user.is_superuser:
            return self.readonly_fields + ('img_width', 'img_height',)
        return self.readonly_fields
