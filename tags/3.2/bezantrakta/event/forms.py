from django.forms import ModelForm

from jsoneditor.forms import JSONEditor

from .models import Event


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ('__all__')
        widgets = {
            'settings': JSONEditor,
        }
