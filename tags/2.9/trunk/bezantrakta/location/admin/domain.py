from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from django.contrib import admin
from django.db.models import TextField
from django.utils.translation import ugettext as _

from jsoneditor.forms import JSONEditor

from ..models import Domain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    actions = ('publish_or_unpublish_items',)
    formfield_overrides = {
        TextField: {'widget': JSONEditor},
    }
    list_display = ('title', 'slug', 'is_published',)
    list_filter = (
        ('city', RelatedDropdownFilter),
    )
    list_per_page = 10
    list_select_related = ('city',)
    search_fields = ('title', 'slug',)

    fieldsets = (
        (
            None,
            {
                'fields': ('id', 'title', 'slug', 'is_published', 'city',),
            }
        ),
        (
            None,
            {
                'fields': ('settings',),
                'classes': ('json_settings',),
                'description': _('domain_settings_help_text'),
            }
        ),
    )

    def publish_or_unpublish_items(self, request, queryset):
        """Пакетная публикация или снятие с публикации сайтов."""
        for item in queryset:
            item.is_published = False if item.is_published else True
            item.save(update_fields=['is_published'])
    publish_or_unpublish_items.short_description = _('domain_admin_publish_or_unpublish_items')
