import os
from django.db import models
from django.conf import settings
import uuid 
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator 
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile




class Player(models.Model): 
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player')
    games_played = models.PositiveIntegerField()
    opponents_met = models.PositiveIntegerField()
    games_won = models.PositiveIntegerField()
    inviting_to_play = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile-pics', default='profile-pics/default.jpg')
    total_points = models.PositiveIntegerField(default=1000)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    
    def get_opponents(self):
        invited = Player.objects.select_related('user').filter(sent_matchup_invitings__player_accepting=self)
        accepted = Player.objects.select_related('user').filter(accepted_matchups__player_inviting=self)
        return (invited | accepted).distinct()


    def save(self, *args, **kwargs):
        updating_image = False
        default_image_path = 'profile-pics/default.jpg'
        print(self.profile_image)
        if self.pk:
            try:
                old_image = Player.objects.get(pk=self.pk).profile_image
                if old_image != self.profile_image:
                    updating_image = True 
            except Player.DoesNotExist:
                pass

        print(updating_image)
        if updating_image:
            if default_image_path != str(old_image.name):
                old_image.delete(save=False)

            if self.profile_image:
                ext = os.path.splitext(self.profile_image.name)[1]
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                self.profile_image.name = unique_filename
                profile_image = Image.open(self.profile_image)

                # Ensure correct mode (convert RGBA -> RGB to avoid transparency issues)
                if profile_image.mode in ("RGBA", "P"):
                    profile_image = profile_image.convert("RGB")

                if profile_image.height > 600 or profile_image.width > 600:
                    output_size = (600, 600)
                    profile_image.thumbnail(output_size)

                    img_io = BytesIO()
                    profile_image.save(img_io, format="JPEG")  # Use "JPEG" or "PNG" explicitly

                    self.profile_image = ContentFile(img_io.getvalue(), name=self.profile_image.name)

        super().save(*args, **kwargs) 


    class Meta:
        indexes = [
            models.Index(fields=['inviting_to_play']),

            models.Index(fields=['total_points', 'inviting_to_play']),
        ]

class PoolHouse(models.Model):
    title = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    room_image = models.ImageField(upload_to='poolhouses', null=True)
    open_time = models.TimeField()
    close_time = models.TimeField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
    
class PoolHouseStaff(models.Model):
    poolhouse = models.ForeignKey(PoolHouse, on_delete=models.CASCADE, related_name='staff')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')

class PoolHouseImage(models.Model):
    image = models.ImageField(upload_to='poolhall-pics')
    poolhouse = models.ForeignKey(PoolHouse, on_delete=models.CASCADE, related_name='pics')

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)

    


class PoolTable(models.Model):
    poolhouse = models.ForeignKey(PoolHouse, on_delete=models.CASCADE, related_name='tables')
    table_id = models.IntegerField(null=True)
    free = models.BooleanField(default=True)
    top = models.FloatField(default=0.0)
    left = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return f'{self.poolhouse.title} - {self.table_id}'
        
    

class GameSession(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    pooltable = models.ForeignKey(PoolTable, on_delete=models.SET_NULL, related_name='game_sessions', null=True)
    players = models.ManyToManyField(Player, through='PlayerGameSession', related_name='game_session')
    status_finished = models.BooleanField(default=False)
    start_time = models.DateTimeField(auto_now_add=True)

class Matchup(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    player_inviting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sent_matchup_invitings')
    player_accepting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='accepted_matchups')
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=True)

    class Meta:
        unique_together = [['player_accepting', 'player_inviting']]


class Reservation(models.Model):
    start_time = models.DateTimeField()
    duration = models.PositiveSmallIntegerField(default=30)
    table = models.ForeignKey(PoolTable, on_delete=models.CASCADE, related_name='reservations')
    player_reserving = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='my_reservations', null=True)
    other_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='other_reservations')
    end_time = models.DateTimeField()
    real_end_datetime = models.DateTimeField()
    finished_reservation = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)
    in_process = models.BooleanField(default=False)


    def __str__(self) -> str:
        return f'{self.start_time} - {self.end_time}'
    
    

class PlayerGameSession(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)


class Invitation(models.Model):
    player_invited = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='received_invitations')
    player_inviting = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sent_invitations')


    class Meta:
        unique_together = [['player_invited', 'player_inviting']]


class InvitationDenied(models.Model):
    player_invited = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_denied = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='denied_invitations')
    timestamp = models.DateTimeField(auto_now_add=True)
    


class Message(models.Model):
    body = models.TextField()
    matchup = models.ForeignKey(Matchup, on_delete=models.CASCADE, related_name='messages')
    time_sent = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(Player, on_delete=models.SET_NULL, related_name='sent_messages', null=True)
    after_outdated = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.body
    


    class Meta:
        indexes = [
            models.Index(fields=['time_sent']),
        ]

    

    


class PoolHouseRating(models.Model):
    rate = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField()
    rater = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='my_ratings')
    poolhouse = models.ForeignKey(PoolHouse, on_delete=models.CASCADE, related_name='ratings')
    timestamp = models.DateTimeField(auto_now=True)



    class Meta:
        unique_together = [['rater', 'poolhouse']]


class History(models.Model):
    winner_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='win_history')
    loser_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='loss_history', null=True)
    result_winner = models.PositiveSmallIntegerField(null=True)
    result_loser = models.PositiveSmallIntegerField(null=True)
    points_given = models.PositiveSmallIntegerField(null=True)
    penalty_points = models.PositiveSmallIntegerField(null=True)
    tie = models.BooleanField(default=False) 
    timestamp = models.DateTimeField(auto_now_add=True)
    poolhouse = models.ForeignKey(PoolHouse, on_delete=models.SET_NULL, null=True, related_name='matches_history')



class NotificationChoices(models.TextChoices):
    INVITED = 'INV', 'Invited'
    REJECTED = 'REJ', 'Rejected'
    ACCEPTED = 'ACP', 'Accepted'
    GAME_SESSION_END = 'GSE', 'Game Session End'
    GAME_SESSION_END_ALONE = 'GSEA', 'Game Session End Alone'
    SET_PASSWORD = 'SPW', 'Set password'

class Notification(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='notifications')
    sent_by = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    body = models.TextField(null=True)
    extra = models.TextField(null=True)
    type = models.CharField(choices=NotificationChoices.choices, max_length=4)

    def __str__(self):
        return f'Notification for {self.player} - {self.type}'