# from django.contrib import admin

# from project.decorators import domain_filter
# from ..models import Event, EventContainerBinder, EventGroup, EventGroupBinder


# class EventGroupBinderInline(admin.TabularInline):
#     model = EventGroupBinder
#     extra = 0
#     fields = ('event',)

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         """
#         Для добавления в группу выводятся только привязанные к выбранному долмену события.
#         """
#         if db_field.name == 'event':
#             domain_filter = request.COOKIES.get('bezantrakta_admin_domain', None)
#             kwargs['queryset'] = Event.objects.filter(domain__slug=domain_filter)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class EventContainerBinderInline(admin.TabularInline):
#     model = EventContainerBinder
#     extra = 0
#     fields = ('event_container', 'order', 'img', 'img_preview',)
#     readonly_fields = ('order', 'img_preview',)
#     radio_fields = {'event_container': admin.VERTICAL, }


# @admin.register(EventGroup)
# class EventGroupAdmin(admin.ModelAdmin):
#     inlines = (EventGroupBinderInline, EventContainerBinderInline,)
#     list_display = ('title', 'is_published', 'container_count', 'domain',)
#     list_select_related = ('domain',)
#     prepopulated_fields = {
#         'slug': ('title',),
#     }

#     @domain_filter('domain__slug')
#     def get_queryset(self, request):
#         return super().get_queryset(request)
