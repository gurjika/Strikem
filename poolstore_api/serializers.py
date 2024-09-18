from datetime import timedelta
from rest_framework import serializers
from poolstore.models import Invitation, Matchup, Message, Player, PoolHouse, PoolTable, Reservation
from django.utils import timezone
from .tasks import send_email_before_res

now = timezone.now()


class SimplePlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['user', 'profile_image', 'games_won']


class ReservationSerializer(serializers.ModelSerializer):
    player = SimplePlayerSerializer(read_only=True)
    class Meta:
        model = Reservation
        fields = ['id', 'start_time', 'player', 'duration']

    def create(self, validated_data):
        player = self.context['player']
        table_id = self.context['table_id']
        end_time = validated_data['start_time'] + timedelta(minutes=validated_data['duration'])
        real_end_datetime = end_time + timedelta(minutes=5)
        start_time = validated_data['start_time']
        existing_reservations = Reservation.objects.filter(table_id=table_id, start_time__range=[start_time - timedelta(hours=3), start_time + timedelta(hours=3)])
        for reservation in existing_reservations:
            if not (validated_data['start_time'] >= reservation.real_end_datetime or real_end_datetime <= reservation.start_time):
                raise serializers.ValidationError('nu kvetav dzma')
    


        send_email_before_res.apply_async((player.user.id,), eta=start_time - timedelta(minutes=20))
        obj = Reservation.objects.create(**validated_data, end_time=end_time, table_id=table_id, player=player, real_end_datetime=real_end_datetime)
        return obj
    


class PoolTableSerializer(serializers.ModelSerializer):
    current_reservation = serializers.SerializerMethodField()
    class Meta:
        model = PoolTable
        fields = ['id', 'current_reservation']

    def get_current_reservation(self, obj):
        ## SHOW ONGOING RESERVATION IF THE SESSION EXISTS
        if obj.game_sessions.first():
            return ReservationSerializer(obj.reservations.filter(end_time__gte=now).first()).data
        return None

class PoolHouseSerializer(serializers.ModelSerializer):
    tables = PoolTableSerializer(many=True)
    class Meta:
        model = PoolHouse
        fields = ['id', 'title', 'address', 'tables']



class MessageSerializer(serializers.ModelSerializer):
    sender = SimplePlayerSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'body', 'time_sent', 'sender']


class MatchupSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    class Meta:
        model = Matchup
        fields = ['id', 'player_inviting', 'player_accepting', 'last_message']


    def get_last_message(self, obj):
        messages = obj.messages
        return MessageSerializer(messages.last()).data
    

class InvitationSerializer(serializers.ModelSerializer):
    player_invited = SimplePlayerSerializer(read_only=True)
    player_inviting = SimplePlayerSerializer(read_only=True)
    class Meta:
        model = Invitation
        fields = ['id', 'player_invited', 'player_inviting']