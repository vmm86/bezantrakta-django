from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from django.contrib import admin
from django.db.models import TextField
from django.utils.translation import ugettext as _

from jsoneditor.forms import JSONEditor

from .forms import CityForm
from .models import City, Domain


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityForm
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'timezone_offset', 'state_icons',)
    list_per_page = 10
    radio_fields = {'state': admin.VERTICAL, }
    search_fields = ('title',)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
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
                'classes': ('domain_settings',),
                'description': _('domain_settings_help_text'),
            }
        ),
    )
