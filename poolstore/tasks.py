from celery import shared_task
from django.contrib.contenttypes.models import ContentType

from poolstore.models import GameSession, Invitation, Message, Notification, Player, InvitationDenied

@shared_task
def create_notification(player, sent_by, type, body=None, extra=None):
    player = Player.objects.get(user__username=player)
    
    if sent_by:
        sent_by = Player.objects.get(user__username=sent_by)

    Notification.objects.create(
        player=player,
        body=body,
        sent_by=sent_by,
        extra=extra,
        type=type,
    )
        



@shared_task
def delete_denied_invite(id):
    invitation_denied = InvitationDenied.objects.get(id=id)
    invitation_denied.delete()