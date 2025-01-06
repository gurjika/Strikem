from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from django.db.models import Q
from poolstore.models import GameSession, Invitation, Message, Notification, Player, InvitationDenied


@shared_task
def invitation_cleanup(player_1, player_2):
    player_1 = Player.objects.get(id=player_1)
    player_2 = Player.objects.get(id=player_2)

    invitations = Invitation.objects.filter(
        Q(player_inviting=player_2, player_invited=player_1) |
        Q(player_inviting=player_1, player_invited=player_2)
    )

    invitations.delete()


@shared_task
def delete_denied_invite(id):
    invitation_denied = InvitationDenied.objects.get(id=id)
    invitation_denied.delete()



@shared_task
def delete_outdated_notifications():
    cutoff_date = now() - timedelta(days=5)
    Notification.objects.filter(timestamp__lt=cutoff_date).delete()