import pytz

from django import forms

from dal import autocomplete

from .models import City, timezone_offset_humanized


def timezones_with_offsets(timezones):
    offsets = ''
    for tz in timezones:
        offsets += '<br>{offset} {timezone}'.format(
            offset=timezone_offset_humanized(pytz.timezone(tz)),
            timezone=tz
        )
    return offsets


class CityForm(forms.ModelForm):
    timezone_list = [tz for tz in pytz.country_timezones('ru')]
    timezone = autocomplete.Select2ListChoiceField(
        choice_list=timezone_list,
        # initial='Europe/Moscow',
        widget=autocomplete.ListSelect2(),
        label='Часовой пояс',
        help_text="""
        <a href="http://www.worldtimezone.com/time-russia24ru.php" target="_blank">
        👉 Поиск часового пояса для конкретного города</a>
        <br>{timezones_with_offsets}
        """.format(timezones_with_offsets=timezones_with_offsets(timezone_list))
    )

    class Meta:
        model = City
        fields = ('__all__')
        autocomplete_fields = ('timezone')
