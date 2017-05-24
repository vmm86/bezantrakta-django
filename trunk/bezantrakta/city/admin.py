from django.contrib import admin

from .models import City
from .forms import CityForm


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityForm
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'timezone', 'status',)
    search_fields = ('title',)
