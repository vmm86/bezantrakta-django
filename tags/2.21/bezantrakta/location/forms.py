import pytz

from django import forms

from dal import autocomplete

from .models import City, timezone_offset_humanized


def timezones_with_offsets(timezones):
    """Вывод текстового списка часовых поясов в Российской Федерации с указанием разницы во времени с ``UTC``.

    Args:
        timezones (TYPE): Список часовых поясов ``pytz``.

    Returns:
        str: Текстовый списока часовых поясов РФ с разницей во времени с ``UTC``.
    """
    offsets = ''
    for tz in timezones:
        offsets += '<br>{offset} {timezone}'.format(
            offset=timezone_offset_humanized(pytz.timezone(tz)),
            timezone=tz
        )
    return offsets


class CityForm(forms.ModelForm):
    """Форма для выбора часовых поясов в выпадающем списке с автозаполнением.

    Attributes:
        timezone_list (list): Список часовых поясов ``pytz``.
        timezone (dal.autocomplete.Select2ListChoiceField): Поле модели с переопределением его виджета.
    """
    timezone_list = [tz for tz in pytz.country_timezones('ru')]
    timezone = autocomplete.Select2ListChoiceField(
        choice_list=timezone_list,
        initial='Europe/Moscow',
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
