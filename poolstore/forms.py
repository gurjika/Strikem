from django import forms
from poolstore.models import Player
from django.conf import settings
from .models import Reservation


class TimeInput(forms.TimeInput):
    input_type = 'time'

class DateInput(forms.DateInput):
    input_type = 'date'


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_time', 'end_time', 'date']

        widgets = {
            'start_time': TimeInput(),
            'end_time': TimeInput(),
            'date': DateInput()
        }