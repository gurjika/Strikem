from rest_framework import serializers
from poolstore.models import PoolHouse, PoolTable, Reservation
from django.utils import timezone
now = timezone.now()


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'start_time', 'player', 'end_time']

class PoolTableSerializer(serializers.ModelSerializer):
    current_reservation = serializers.SerializerMethodField()
    class Meta:
        model = PoolTable
        fields = ['id', 'current_reservation']

    def get_current_reservation(self, obj):
        if obj.game_sessions.first():
            return ReservationSerializer(obj.reservations.filter(start_time__gte=now).first()).data
        return None

class PoolHouseSerializer(serializers.ModelSerializer):
    tables = PoolTableSerializer(many=True)
    class Meta:
        model = PoolHouse
        fields = ['id', 'title', 'address', 'tables']