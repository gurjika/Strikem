from django import forms
from poolstore.models import Player
from django.conf import settings
from .models import Reservation
from datetime import date, timedelta
from django.utils import timezone
from datetime import datetime



current_time = timezone.now().time()
min_time = current_time.strftime('%H:%M') 


min_value_date = date.today()
min_value_date_format = min_value_date.strftime('%Y-%m-%d')

max_value_date = min_value_date + timedelta(days=3)
max_value_date_format = max_value_date.strftime('%Y-%m-%d')

class TimeInput(forms.TimeInput):
    input_type = 'time'


    

class DateInput(forms.DateInput):
    input_type = 'date'


DURATION_CHOICES = [
    ('30', '30 MINUTES'),
    ('60', '1 HOUR'),
    ('90', '1 HOUR AND 30 MINUTES'),
    ('120', '2 HOURS'),
]


class ReservationForm(forms.ModelForm):

    duration = forms.ChoiceField(
    choices=DURATION_CHOICES,
    label='Select Duration',
    widget=forms.RadioSelect(attrs={
        'class': 'form-check-input',
    })
    )

    class Meta:
        model = Reservation
        fields = ['start_time', 'duration', 'date']

        widgets = {
            'start_time': TimeInput(attrs={'class': 'form-control', 'id': 'start_time', 'min': '10:00', 'max': '02:00'}),
            'date': DateInput(
                attrs={
                    'class': 'form-control datepicker', 
                    'min': min_value_date_format,
                    'max': max_value_date_format,
                    'id': 'date'},),
        }
        
   

        