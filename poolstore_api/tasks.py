from celery import shared_task
from channels.layers import get_channel_layer
from poolstore.models import GameSession
from asgiref.sync import async_to_sync

@shared_task
def finish_game_session(game_session_id):
    game_session = GameSession.objects.get(id=game_session_id)
    channel_layer = get_channel_layer()
    group_name = f'session_{game_session.id}'
    
    event = {
        'type': 'finish_game_session',
    }

    async_to_sync(channel_layer.group_send)(group_name, event)
    game_session.delete()


