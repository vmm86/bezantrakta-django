from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from .forms import CityForm
from .models import City
from .models import Domain


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityForm
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'timezone',)
    search_fields = ('title',)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published',)
    list_filter = (
        ('city', RelatedDropdownFilter),
    )
    list_select_related = ('city',)
    search_fields = ('title', 'slug',)
