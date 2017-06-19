from django.contrib import admin
from django.db.models import TextField

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from jsoneditor.forms import JSONEditor

from .forms import CityForm
from .models import City
from .models import Domain


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityForm
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'timezone', 'state_icons',)
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
