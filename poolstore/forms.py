from typing import Any
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
            'start_time': TimeInput(attrs={'class': 'form-control', 'id': 'start_time', 'min': '10:00', 'max': '04:00'}),
            'date': DateInput(
                attrs={
                    'class': 'form-control datepicker', 
                    'hx-trigger': 'input',
                    'hx-get': '/reservations/',
                    'hx-target': '#reservations',
                    'min': min_value_date_format,
                    'max': max_value_date_format,
                    'id': 'date'
                    })}
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.now()
        self.fields['date'].initial = now.date()
   

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        duration = cleaned_data.get('duration')

        start_datetime = datetime.combine(date, start_time)
        end_datetime = start_datetime + timedelta(minutes=int(duration))
        real_end_datetime = end_datetime + timedelta(minutes=5)

        # Check for overlapping reservations
        existing_reservations = Reservation.objects.filter(
            date=date,
        ).exclude(id=self.instance.id)


        
        for reservation in existing_reservations:
            existing_start = datetime.combine(reservation.date, reservation.start_time)
            existing_end = datetime.combine(reservation.date, reservation.real_end_time)
            overlap_check = False
            
    
            if not (start_datetime >= existing_end or real_end_datetime <= existing_start):
                raise forms.ValidationError('Error1')

   

         
                
        return cleaned_data
        