from django.db import models
from django.conf import settings
import uuid 

# Create your models here.

class Player(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player')
    games_played = models.PositiveIntegerField()
    opponents_met = models.PositiveIntegerField()
    games_won = models.PositiveIntegerField()
    inviting_to_play = models.BooleanField(default=False)

class PoolHouse(models.Model):
    title = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    

class MatchMake(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matchmakings')
    time_created = models.DateTimeField(auto_now_add=True)
    
    
class PoolTable(models.Model):
    poolhouse = models.ForeignKey(PoolHouse, on_delete=models.CASCADE, related_name='tables')


class GameSession(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    pooltable = models.ForeignKey(PoolTable, on_delete=models.SET_NULL, related_name='game_sessions', null=True)
    players = models.ManyToManyField(Player, through='PlayerGameSession', related_name='game_session')
    result = models.CharField(max_length=50)

class Reservation(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)

class Rating(models.Model):
    pass
    
class PlayerGameSession(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)


class Invitation(models.Model):
    player_invited = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='received_invitations')
    player_inviting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sent_invitations')

class Matchup(models.Model):
    player_inviting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sent_matchup_invitings')
    player_accepting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='accepted_matchups')