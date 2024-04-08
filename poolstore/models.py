from django.db import models
from django.conf import settings
# Create your models here.

class Player(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player')
    games_played = models.PositiveIntegerField()
    opponents_met = models.PositiveIntegerField()
    games_won = models.PositiveIntegerField()

class PoolHouse(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    
    
class PoolTable(models.Model):
    poolhouse = models.ForeignKey(PoolHouse, on_delete=models.CASCADE, related_name='tables')


class GameSession(models.Model):
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