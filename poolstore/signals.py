from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, Notification, NotificationChoices




@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_player_for_new_user(sender, instance, created, **kwargs):
    if created:
        if not instance.is_staff:
            player = Player.objects.create(user=instance, games_played=0, opponents_met=0, games_won=0)

            if not bool(instance.password):
                Notification.objects.create(player=player, sent_by=None, body='Please set your account password to fully access its features', type=NotificationChoices.SET_PASSWORD)

