import pytz

from django import forms

from dal import autocomplete

from .models import City


def get_timezone_list():
    return [tz for tz in pytz.country_timezones('ru')]


class CityForm(forms.ModelForm):
    timezone = autocomplete.Select2ListChoiceField(
        choice_list=get_timezone_list,
        # initial='Europe/Moscow',
        widget=autocomplete.ListSelect2(),
        label='Часовой пояс',
        help_text="""
        <a href="https://askgeo.com/" target="_blank">👉 Поиск часового пояса для конкретного города</a>
        """
    )

    class Meta:
        model = City
        fields = ('__all__')
        autocomplete_fields = ('timezone')
