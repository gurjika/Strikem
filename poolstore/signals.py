from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Matchup


@receiver(post_save, sender=Matchup)
def remove_player_from_matchmake_list_on_accept(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = 'matchmake'
        event = {
            'type': 'accepting_player_cleanup',
            'accepter_username': instance.player_accepting.user.username

        }

        async_to_sync(channel_layer.group_send)(group_name, event)