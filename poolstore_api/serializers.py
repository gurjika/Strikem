from datetime import timedelta
from rest_framework import serializers
from poolstore.models import GameSession, History, Invitation, Matchup, Message, Player, PoolHouse, PoolHouseImage, PoolHouseRating, PoolTable, Reservation
from django.utils import timezone
from .tasks import send_email_before_res, start_game_session
from django.contrib.auth import get_user_model
from django.db import transaction

now = timezone.now()

User = get_user_model()

PENALTY_POINTS = 2
WIN_POINTS = 10
TIE_POINTS = 1





class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'id', 'username']


class PlayerSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    inviting_to_play = serializers.BooleanField(read_only=True)
    opponents_met = serializers.IntegerField(read_only=True)
    games_played = serializers.IntegerField(read_only=True)
    games_won = serializers.IntegerField(read_only=True)
    total_points = serializers.IntegerField(read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'games_played', 'opponents_met', 'games_won', 'inviting_to_play', 'profile_image', 'user', 'total_points']


class SimplePlayerSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    class Meta:
        model = Player
        fields = ['user', 'profile_image', 'total_points']


class ReservationSerializer(serializers.ModelSerializer):
    player_reserving = SimplePlayerSerializer(read_only=True)
    other_player = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), write_only=True)
    other_player_details = SimplePlayerSerializer(source='other_player', read_only=True)
    finished_reservation = serializers.BooleanField(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'start_time', 'player_reserving', 'duration', 'other_player', 'other_player_details', 'finished_reservation']

    def validate(self, data):
        if self.context['player'] == data['other_player']:
            raise serializers.ValidationError('Same Player Error')
        return data
    

    def create(self, validated_data):
        player_reserving = self.context['player']
        table_id = self.context['table_id']
        end_time = validated_data['start_time'] + timedelta(minutes=validated_data['duration'])
        real_end_datetime = end_time + timedelta(minutes=5)
        start_time = validated_data['start_time']
        existing_reservations = Reservation.objects.filter(table_id=table_id, start_time__range=[start_time - timedelta(hours=3), start_time + timedelta(hours=3)], finished_reservation=False)
        for reservation in existing_reservations:
            if not (validated_data['start_time'] >= reservation.real_end_datetime or real_end_datetime <= reservation.start_time):
                raise serializers.ValidationError('nu kvetav dzma')
    

        send_email_before_res.apply_async((player_reserving.user.id,), eta=start_time - timedelta(minutes=20))
        obj = Reservation.objects.create(**validated_data, end_time=end_time, table_id=table_id, player_reserving=player_reserving, real_end_datetime=real_end_datetime)
        start_game_session.apply_async((obj.id,), eta=start_time, task_id=f'custom_task_id_{obj.id}')


        return obj
    


class PoolTableSerializer(serializers.ModelSerializer):
    current_session = serializers.SerializerMethodField()
    free = serializers.BooleanField(read_only=True)
    class Meta:
        model = PoolTable
        fields = ['id', 'current_session', 'free']

    def get_current_session(self, obj):
        ## SHOW ONGOING RESERVATION IF THE ACTIVE SESSION EXISTS
        if not obj.free:
            for session in obj.game_sessions.all():
                if not session.status_finished:
                    return ReservationSerializer(obj.reservations.filter(end_time__gte=now).first()).data
        return None
    


class PoolHouseImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)
    pics_upload = serializers.ListField(
        child=serializers.ImageField(), 
        write_only=True
    )
    class Meta:
        model = PoolHouseImage
        fields = ['id', 'image', 'pics_upload']



    def create(self, validated_data):
        images = validated_data.pop('pics_upload')
        poolhouse = PoolHouse.objects.get(id=self.context['poolhouse_id'])
        poolhouse_images = [
            PoolHouseImage(poolhouse=poolhouse, image=image) for image in images
        ]
        PoolHouseImage.objects.bulk_create(poolhouse_images)


        return poolhouse

class PoolHouseSerializer(serializers.ModelSerializer):
    tables = PoolTableSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    pics = PoolHouseImageSerializer(read_only=True, many=True)
    table_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = PoolHouse
        fields = ['id', 'title', 'address', 'tables', 'avg_rating', 'latitude', 'longitude', 'pics', 'table_count']

class SimplePoolHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoolHouse
        fields = ['id', 'title', 'address']


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

class PoolHouseRatingSerializer(serializers.ModelSerializer):
    rater = SimplePlayerSerializer(read_only=True)
    poolhouse = SimplePoolHouseSerializer(read_only=True)
    class Meta:
        model = PoolHouseRating
        fields = ['id', 'rate', 'rater', 'poolhouse', 'review']

    
    def validate_rate(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError('Enter a valid rating')
        return value



    def create(self, validated_data):
        obj, created = PoolHouseRating.objects.update_or_create(
            rater=self.context['player'],
            poolhouse_id=self.context['poolhouse_pk'],
            defaults={
                'review':validated_data['review'],
                'rate': validated_data['rate'],
            }
        )


        return obj
    
class CreateHistorySerializer(serializers.ModelSerializer):
    game_session = serializers.UUIDField(write_only=True)
    class Meta:
        model = History
        fields = ['id', 'game_session', 'winner_player', 'loser_player', 'result_winner', 'result_loser']


    # CHECK IF THE GAME SESSION IS FINISHED AND THE REQUEST IS SENT BY THE PLAYER THAT IS IN THE SESSION

    def validate(self, data):
        game_session_player_ids = GameSession.objects.filter(id=data['game_session'], status_finished=True).values_list('players', flat=True)
        print(game_session_player_ids)
        print(data['loser_player'])
        if data['loser_player'].id in game_session_player_ids and data['winner_player'].id in game_session_player_ids and self.context['player_id'] in game_session_player_ids:
            return data
        raise serializers.ValidationError('Player ids not provided correctly')
    

    # def validate_game_session(self, value):
    #     game_session = GameSession.objects.filter(id=value).filter(players__id__in=[self.context['player_id']], status_finished=True)
    #     if game_session.exists():
    #         return game_session.first()
        
    #     raise serializers.ValidationError('Game Session Does not exist')
    

    def create(self, validated_data):
        try:
            with transaction.atomic():
                game_session = GameSession.objects.get(id=validated_data['game_session'])
                validated_data.update({'poolhouse': game_session.pooltable.poolhouse})
                validated_data.pop('game_session')

                if int(validated_data['result_winner']) == int(validated_data['result_loser']):
                    obj = History.objects.create(tie=True, penalty_points=0, points_given=TIE_POINTS,  **validated_data)
                    
                    player_tie_f = validated_data['winner_player']
                    player_tie_s = validated_data['loser_player']

                    player_tie_f.total_points += TIE_POINTS
                    player_tie_s.total_points += TIE_POINTS

                    player_tie_f.save()
                    player_tie_s.save()
                    return obj


                player_winner = validated_data['winner_player']
                player_winner.total_points += WIN_POINTS

                player_loser = validated_data['loser_player']
                player_loser.total_points -= PENALTY_POINTS

                player_loser.save()
                player_winner.save()

                game_session.delete()

                return History.objects.create(penalty_points=PENALTY_POINTS, points_given=WIN_POINTS, **validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error occurred: {str(e)}")

        
    
class ListHistorySerializer(serializers.ModelSerializer):
    poolhouse = SimplePoolHouseSerializer()
    winner_player = SimplePlayerSerializer()
    loser_player = SimplePlayerSerializer()
    class Meta:
        model = History
        fields = ['winner_player', 'loser_player', 'result_winner',
                  'result_loser', 'points_given', 'penalty_points', 'tie', 'timestamp', 
                  'poolhouse']



class GameSessionSerializer(serializers.ModelSerializer):
    players = SimplePlayerSerializer(many=True)

    class Meta:
        model = GameSession
        fields = ['id', 'pooltable', 'players', 'status_finished']


class StaffReservationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = ['table_id', 'duration', 'start_time']


    def create(self, validated_data):
        table = PoolTable.objects.get(table_id=validated_data['table_id'], poolhouse=['poolhouse_pk'])
        return Reservation.objects.create(table=table, **validated_data)

