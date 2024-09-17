from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.db.models import F
import uuid 
from django.utils.text import slugify
from PIL import Image
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.


class Player(models.Model): 
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player')
    games_played = models.PositiveIntegerField()
    opponents_met = models.PositiveIntegerField()
    games_won = models.PositiveIntegerField()
    inviting_to_play = models.BooleanField(default=False)
    profile_image = models.ImageField(default='default.jpg', upload_to='profile-pics')
    
    
    def get_opponents(self):
        invited = Player.objects.select_related('user').filter(sent_matchup_invitings__player_accepting=self)
        accepted = Player.objects.select_related('user').filter(accepted_matchups__player_inviting=self)
        return (invited | accepted).distinct()

    def save(self, *args, **kwargs):
        super().save()

        if self.profile_image:
            profile_image = Image.open(self.profile_image.path)

            if profile_image.height > 600 or profile_image.width > 600:
                output_isze = (300, 300)
                profile_image.thumbnail(output_isze)
                profile_image.save(self.profile_image.path)


class PoolHouse(models.Model):
    title = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


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
    start_time = models.DateTimeField()
    duration = models.PositiveSmallIntegerField(default=30)
    table = models.ForeignKey(PoolTable, on_delete=models.CASCADE, related_name='reservations')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='reservations')
    end_time = models.DateTimeField()
    real_end_datetime = models.DateTimeField()


    def __str__(self) -> str:
        return f'{self.start_time} - {self.end_time}'
    


class Rating(models.Model):
    rate = models.PositiveSmallIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    

class PlayerGameSession(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)


class Invitation(models.Model):
    player_invited = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='received_invitations')
    player_inviting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sent_invitations')


class Matchup(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    player_inviting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sent_matchup_invitings')
    player_accepting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='accepted_matchups')
    


class Message(models.Model):
    body = models.TextField()
    matchup = models.ForeignKey(Matchup, on_delete=models.CASCADE, related_name='messages')
    time_sent = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(Player, on_delete=models.SET_NULL, related_name='sent_messages', null=True)
    after_outdated = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.body
    
