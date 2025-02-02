from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, Notification, NotificationChoices


# @receiver(post_save, sender=Matchup)
# def remove_player_from_matchmake_list_on_accept(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = get_channel_layer()
#         group_name = 'matchmake'
        
#         event = {
#             'type': 'accepting_player_cleanup',
#             'accepter_username': instance.player_accepting.user.username,
#             'inviter_username': instance.player_inviting.user.username,
#         }

#         async_to_sync(channel_layer.group_send)(group_name, event)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_player_for_new_user(sender, instance, created, **kwargs):
    if created:
        if not instance.is_staff:
            player = Player.objects.create(user=instance, games_played=0, opponents_met=0, games_won=0)

            if not instance.has_usable_password():
                Notification.objects.create(player=player, sent_by=None, body='Please set your account password to fully access its features', type=NotificationChoices.SET_PASSWORD)

