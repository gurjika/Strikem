import django_filters
from poolstore.models import Reservation

class ReservationFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='start_time', lookup_expr='date')

    class Meta:
        model = Reservation
        fields = ['start_date']