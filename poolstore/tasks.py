from datetime import timedelta
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from poolstore.models import GameSession, Invitation, Message, Notification, Player, InvitationDenied





@shared_task
def delete_denied_invite(id):
    invitation_denied = InvitationDenied.objects.get(id=id)
    invitation_denied.delete()



@shared_task
def delete_outdated_notifications():
    cutoff_date = now() - timedelta(days=5)
    Notification.objects.filter(timestamp__lt=cutoff_date).delete()