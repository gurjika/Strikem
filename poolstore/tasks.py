from celery import shared_task
from django.contrib.contenttypes.models import ContentType

from poolstore.models import GameSession, Invitation, Message, Notification, Player, InvitationDenied





@shared_task
def delete_denied_invite(id):
    invitation_denied = InvitationDenied.objects.get(id=id)
    invitation_denied.delete()