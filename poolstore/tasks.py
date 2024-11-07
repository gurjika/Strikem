from celery import shared_task
from django.contrib.contenttypes.models import ContentType

from poolstore.models import GameSession, Invitation, Message, Notification, Player, InvitationDenied

@shared_task
def create_notification(player, content_type, object_id, body=None):
    player = Player.objects.get(user__username=player)

    content_type_model = {
        'message': Message,
        'invitation': Invitation,
    }

    content_type = content_type_model.get(content_type)


    if body:
        Notification.objects.create(
        player=player,
        body=body,
    )
        
    else:
        Notification.objects.create(
            player=player,
            content_type=ContentType.objects.get_for_model(content_type),
            object_id=object_id
        )



@shared_task
def delete_denied_invite(id):
    invitation_denied = InvitationDenied.objects.get(id=id)
    invitation_denied.delete()